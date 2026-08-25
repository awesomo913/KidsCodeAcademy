"""Kids Code Academy — sandboxed coding tutorial for ages 7+.

Loads the kid-themed tutorial HTML in a native pywebview window.
All AI helpers (Claude / Cursor / Gemini) are pre-scripted JSON — zero network.
Bundled into a single .exe with PyInstaller.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
from pathlib import Path

import webview

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("KidsCodeAcademy")

# Crash logger (Crash Logger Rule). Best-effort; never block app launch on import.
try:
    sys.path.insert(0, str(Path.home() / ".claude" / "scripts"))
    from crash_logger import install as _install_crash, log_event as _log_event  # type: ignore
    _PROJECT_ROOT = Path(__file__).resolve().parent
    _install_crash(project_root=_PROJECT_ROOT)
    _log_event("info", "app.boot", {"frozen": getattr(sys, "frozen", False)})
except Exception as _exc:  # pragma: no cover
    log.info("crash_logger not available: %s", _exc)
    # No-op fallback so call sites can use _log_event unconditionally.
    def _log_event(*_args: object, **_kwargs: object) -> None:  # type: ignore[no-redef]
        return None

APP_TITLE = "Kids Code Academy"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 860
MIN_WIDTH = 800
MIN_HEIGHT = 600
HTML_FILENAME = "index.html"


def get_base_dir() -> Path:
    """Resolve resource base path for both dev and frozen (PyInstaller) modes."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def _appdata_root() -> Path:
    """Stable per-user app data root.

    Cross-platform layout:
      - Windows: %APPDATA%/KidsCodeAcademy/  (e.g. C:/Users/<u>/AppData/Roaming/KidsCodeAcademy)
      - Linux / Raspberry Pi: $XDG_DATA_HOME/KidsCodeAcademy/  or  ~/.local/share/KidsCodeAcademy/
      - macOS:  ~/Library/Application Support/KidsCodeAcademy/
    """
    if os.name == "nt":  # Windows
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        root = Path(appdata) / "KidsCodeAcademy"
    elif sys.platform == "darwin":  # macOS
        root = Path.home() / "Library" / "Application Support" / "KidsCodeAcademy"
    else:  # Linux / Raspberry Pi / other Unix
        xdg = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg) if xdg else (Path.home() / ".local" / "share")
        root = base / "KidsCodeAcademy"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_user_data_dir() -> Path:
    """Writable per-user folder for kid project saves (Lesson 16)."""
    user_dir = _appdata_root() / "kid_projects"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_state_file() -> Path:
    """File-backed mirror of the kid's localStorage. Belt-and-suspenders persistence
    in case the WebView2 storage gets wiped (PyInstaller --onefile changes the
    _MEI temp path on every launch, which used to invalidate WebView2 storage).
    """
    return _appdata_root() / "state.json"


def get_webview_storage_path() -> Path:
    """Stable storage_path for pywebview's WebView2 user data folder.
    Default pywebview private_mode=True wipes localStorage on close — we override
    it with a real persistent directory under %APPDATA%.
    """
    p = _appdata_root() / "webview_data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _render_project_view(obj: object, stem: str) -> str:
    """Build a standalone viewer HTML for a saved kid project that has no
    pre-rendered HTML twin (v0.7.15). Two shapes handled:

      - level save: {"grid": ["#..#", "..@.", ...], "savedAt": "..."} →
        render the painted grid as a colored table.
      - anything else → pretty-print the JSON fields.

    Always returns valid HTML so the Parent Corner 'Open' button shows
    something instead of silently launching an unassociated .json.
    """
    import html as _html
    import json as _json

    title = _html.escape(stem.replace("kid_level_", "My Level "))
    cell_colors = {
        "#": "#666", ".": "#fff", "*": "#ffd95e",
        "F": "#4caf50", "@": "#6c5ce7", " ": "#fff",
    }
    body = ""

    grid = obj.get("grid") if isinstance(obj, dict) else None
    if isinstance(grid, list) and grid:
        rows_html = []
        for row in grid:
            cells = "".join(
                f"<td style='width:24px;height:24px;background:{cell_colors.get(ch, '#eee')};"
                f"border:1px solid #ddd;'></td>"
                for ch in str(row)
            )
            rows_html.append(f"<tr>{cells}</tr>")
        legend = (
            "<p style='color:#666;font-size:13px;'>"
            "<b style='color:#6c5ce7;'>■</b> hero &nbsp; "
            "<b style='color:#4caf50;'>■</b> flag &nbsp; "
            "<b style='color:#ffd95e;'>■</b> coin &nbsp; "
            "<b style='color:#666;'>■</b> wall</p>"
        )
        saved = ""
        if isinstance(obj, dict) and obj.get("savedAt"):
            saved = f"<p style='color:#999;'>Saved {_html.escape(str(obj['savedAt'])[:10])}</p>"
        body = (
            f"<h1>{title}</h1>{saved}"
            f"<table style='border-collapse:collapse;margin:16px 0;'>{''.join(rows_html)}</table>"
            f"{legend}"
        )
    else:
        try:
            pretty = _json.dumps(obj, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            pretty = str(obj)
        body = (
            f"<h1>{title}</h1>"
            f"<pre style='background:#f0f0f4;padding:14px;border-radius:8px;"
            f"overflow:auto;font-size:13px;'>{_html.escape(pretty)}</pre>"
        )

    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{title}</title>"
        "<style>body{font-family:'Segoe UI',system-ui,sans-serif;background:#faf7f2;"
        "color:#2a2a2a;max-width:680px;margin:0 auto;padding:28px;}"
        "h1{color:#6c5ce7;}@media print{body{background:#fff;}}</style></head>"
        f"<body>{body}<p style='margin-top:28px;color:#999;font-size:12px;'>"
        "Made in Kids Code Academy. Save or print this page!</p></body></html>"
    )


class JSBridge:
    """JS-callable bridge.

    Exposes:
      - save_kid_project(name, data)   — Lesson 16 SVG saves
      - save_state(json_blob)          — mirror localStorage to state.json
      - load_state() -> str            — read state.json (empty if missing)
      - clear_state()                  — wipe state.json (Reset all progress)
      - list_kid_projects() / open_kid_project(name) — Parent Corner Projects tab
    """

    def get_user_dir(self) -> str:
        return str(get_user_data_dir())

    def save_kid_project(self, filename: str, data: str) -> dict:
        safe_name = "".join(c for c in filename if c.isalnum() or c in ("_", "-", "."))
        if not safe_name:
            return {"ok": False, "error": "invalid filename"}
        target = get_user_data_dir() / safe_name
        try:
            target.write_text(data, encoding="utf-8")
        except OSError as exc:
            log.warning("save_kid_project failed: %s", exc)
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "path": str(target)}

    def save_state(self, json_blob: str) -> dict:
        """Atomically write state.json. JS calls this on every progress update."""
        if not isinstance(json_blob, str):
            return {"ok": False, "error": "json_blob must be a string"}
        # Cap at 4 MB defensively — kid state should never approach this
        if len(json_blob) > 4 * 1024 * 1024:
            return {"ok": False, "error": "state too large"}
        target = get_state_file()
        tmp = target.with_suffix(".json.tmp")
        t0 = time.monotonic()
        try:
            tmp.write_text(json_blob, encoding="utf-8")
            os.replace(tmp, target)  # atomic on Windows + POSIX
        except OSError as exc:
            log.warning("save_state failed: %s", exc)
            _log_event("boundary", "save_state", {"target": str(target), "ok": False, "err": str(exc)})
            return {"ok": False, "error": str(exc)}
        ms = (time.monotonic() - t0) * 1000.0
        # Visible on stdout/stderr so headless workflow artifacts capture the proof.
        log.info("save_state ok bytes=%d path=%s (%.1fms)", len(json_blob), target, ms)
        _log_event("boundary", "save_state", {"target": str(target), "ok": True, "ms": round(ms, 1), "bytes": len(json_blob)})
        return {"ok": True, "path": str(target)}

    def load_state(self) -> str:
        """Return state.json contents as a string (empty if no file)."""
        target = get_state_file()
        if not target.is_file():
            log.info("load_state: no file at %s (fresh install)", target)
            _log_event("boundary", "load_state", {"target": str(target), "ok": True, "exists": False})
            return ""
        t0 = time.monotonic()
        try:
            data = target.read_text(encoding="utf-8")
        except OSError as exc:
            log.warning("load_state failed: %s", exc)
            _log_event("boundary", "load_state", {"target": str(target), "ok": False, "err": str(exc)})
            return ""
        ms = (time.monotonic() - t0) * 1000.0
        log.info("load_state ok bytes=%d path=%s (%.1fms)", len(data), target, ms)
        _log_event("boundary", "load_state", {"target": str(target), "ok": True, "ms": round(ms, 1), "bytes": len(data)})
        return data

    def clear_state(self) -> dict:
        """Delete state.json. Called only on explicit Reset all progress."""
        target = get_state_file()
        try:
            if target.is_file():
                target.unlink()
        except OSError as exc:
            log.warning("clear_state failed: %s", exc)
            return {"ok": False, "error": str(exc)}
        return {"ok": True}

    # ── v0.7.15: parent-supplied background music ──────────────────────────
    # The bundled assets/bg_music/ is read-only (PyInstaller _MEIPASS), so a
    # parent's own track is copied into AppData and served to the player as a
    # base64 data URL on demand (kept OUT of localStorage so state.json never
    # bloats with megabytes of audio).

    def pick_music_file(self) -> dict:
        """Open a native file picker; copy the chosen audio into AppData as
        user_bg_music<ext>. Returns {ok, name, ext} or {ok:False,...}.
        """
        import shutil
        try:
            import webview  # local import keeps module import-safe in dev
            windows = getattr(webview, "windows", None) or []
            if not windows:
                return {"ok": False, "error": "no window"}
            win = windows[0]
            file_types = ("Audio files (*.ogg;*.mp3;*.wav;*.m4a)", "All files (*.*)")
            result = win.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        except Exception as exc:  # pywebview dialog can raise on some backends
            log.warning("pick_music_file dialog failed: %s", exc)
            _log_event("boundary", "pick_music_file", {"ok": False, "err": str(exc)})
            return {"ok": False, "error": str(exc)}
        if not result:
            return {"ok": False, "error": "cancelled"}
        chosen = Path(result[0] if isinstance(result, (list, tuple)) else result)
        ext = chosen.suffix.lower() or ".ogg"
        if ext not in (".ogg", ".mp3", ".wav", ".m4a"):
            return {"ok": False, "error": "unsupported file type"}
        # Cap at 12 MB — a between-lessons loop should be tiny; refuse a full album.
        try:
            if chosen.stat().st_size > 12 * 1024 * 1024:
                return {"ok": False, "error": "file too big (max 12 MB)"}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}
        # Clear any prior user track (different ext) so only one exists.
        for old in _appdata_root().glob("user_bg_music.*"):
            try:
                old.unlink()
            except OSError as exc:
                # Locked file (being read?) would leave two tracks; glob order
                # could then play the wrong one. Surface it loudly.
                log.warning("pick_music_file: could not remove old track %s: %s", old, exc)
        dest = _appdata_root() / f"user_bg_music{ext}"
        try:
            shutil.copy2(chosen, dest)
        except OSError as exc:
            log.warning("pick_music_file copy failed: %s", exc)
            _log_event("boundary", "pick_music_file", {"ok": False, "err": str(exc)})
            return {"ok": False, "error": str(exc)}
        _log_event("boundary", "pick_music_file", {"ok": True, "name": chosen.name, "ext": ext})
        return {"ok": True, "name": chosen.name, "ext": ext}

    def get_user_music(self) -> str:
        """Return the parent's saved track as a base64 data URL, or '' if none.
        Read on demand by the Ambient player so the bytes never touch
        localStorage / state.json.
        """
        import base64
        for fp in _appdata_root().glob("user_bg_music.*"):
            try:
                # Guard the read path too (not just pick): a 12 MB file becomes
                # ~16 MB base64 over the pywebview bridge. Refuse oversize so the
                # bridge doesn't silently drop/truncate an enormous response.
                if fp.stat().st_size > 12 * 1024 * 1024:
                    log.warning("get_user_music: %s too big (%d bytes), skipping", fp, fp.stat().st_size)
                    return ""
                data = fp.read_bytes()
            except OSError as exc:
                log.warning("get_user_music read failed: %s", exc)
                return ""
            ext = fp.suffix.lower().lstrip(".")
            mime = {"ogg": "audio/ogg", "mp3": "audio/mpeg",
                    "wav": "audio/wav", "m4a": "audio/mp4"}.get(ext, "audio/ogg")
            b64 = base64.b64encode(data).decode("ascii")
            return f"data:{mime};base64,{b64}"
        return ""

    def has_user_music(self) -> bool:
        return any(_appdata_root().glob("user_bg_music.*"))

    def list_kid_projects(self) -> list[dict]:
        """v0.7.11 Fix 10: enumerate saved capstone JSON projects.

        Walks kid_projects/ looking for *.json files saved by the share-card
        handler in lesson 60. Returns one entry per project with name, filename,
        and ISO created date. Used by Parent Corner 'Projects' tab.

        Best-effort: any unreadable / non-JSON file is skipped silently
        (kid scribbles or older TXT shares would otherwise crash the list).
        """
        import json
        user_dir = get_user_data_dir()
        items: list[dict] = []
        try:
            for fp in sorted(user_dir.glob("*.json")):
                try:
                    raw = fp.read_text(encoding="utf-8")
                    obj = json.loads(raw)
                except (OSError, json.JSONDecodeError):
                    continue
                # Friendly name: capstone uses game_name; level saves get a
                # readable "My Level" + date instead of the raw kid_level_<ts>.
                stem = fp.stem
                if obj.get("game_name"):
                    nice = str(obj["game_name"])
                elif stem.startswith("kid_level_"):
                    nice = "My Level"
                else:
                    nice = stem
                items.append({
                    "filename": fp.name,
                    "name": nice,
                    "created": str(obj.get("created_at") or obj.get("savedAt") or ""),
                    "kind": str(obj.get("kind") or ("level" if "grid" in obj else "project")),
                })
        except OSError as exc:
            log.warning("list_kid_projects failed: %s", exc)
            _log_event("boundary", "list_kid_projects", {"target": str(user_dir), "ok": False, "err": str(exc)})
            return []
        _log_event("boundary", "list_kid_projects", {"target": str(user_dir), "ok": True, "count": len(items)})
        return items

    def open_kid_project(self, filename: str) -> dict:
        """Open a saved project in the default browser.

        v0.7.15 fix: the original code fell back to launching the raw .json when
        no HTML sibling existed. On Windows .json usually has no GUI association,
        so 'Open' silently did nothing for the kid_level_*.json saves (which have
        no HTML twin). Now we GENERATE a viewer HTML on the fly for any project
        that lacks one — rendering the painted grid for level saves, or a
        pretty field view otherwise — and open that. HTML always has a browser
        association, so Open always shows something.

        Path-safe: only files within get_user_data_dir() are touched.
        """
        import json
        import subprocess
        safe_name = "".join(c for c in filename if c.isalnum() or c in ("_", "-", "."))
        if not safe_name:
            return {"ok": False, "error": "invalid filename"}
        user_dir = get_user_data_dir()
        target = user_dir / safe_name
        html_sibling = target.with_suffix(".html")

        chosen = None
        if html_sibling.is_file():
            chosen = html_sibling
        elif target.is_file():
            # No HTML twin — generate a viewer from the JSON.
            try:
                obj = json.loads(target.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                log.warning("open_kid_project parse failed: %s", exc)
                obj = None
            view = user_dir / (target.stem + "_view.html")
            try:
                view.write_text(_render_project_view(obj, target.stem), encoding="utf-8")
                chosen = view
            except OSError as exc:
                log.warning("open_kid_project view-write failed: %s", exc)
                _log_event("boundary", "open_kid_project", {"target": str(view), "ok": False, "err": str(exc)})
                return {"ok": False, "error": str(exc)}
        else:
            return {"ok": False, "error": "file not found"}

        try:
            if os.name == "nt":  # Windows
                os.startfile(str(chosen))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(chosen)])
            else:
                subprocess.Popen(["xdg-open", str(chosen)])
        except OSError as exc:
            log.warning("open_kid_project failed: %s", exc)
            _log_event("boundary", "open_kid_project", {"target": str(chosen), "ok": False, "err": str(exc)})
            return {"ok": False, "error": str(exc)}
        _log_event("boundary", "open_kid_project", {"target": str(chosen), "ok": True})
        return {"ok": True, "path": str(chosen)}


def _start_local_http_server(serve_dir: Path) -> int:
    """Spin up a tiny loopback HTTP server pointed at serve_dir; return the
    randomly-assigned port.

    Why: on Linux/Pi, WebKitGTK 2.40+ sandboxes file:// URLs and silently
    blocks fetch() of sibling resources (lessons/*.json, assets/*.wav).
    Loading the bundle over http://127.0.0.1:<port>/ sidesteps that —
    everything runs from a real origin. Same code path works on Windows too;
    no functional difference, and it future-proofs against any
    WebView2 file-URL tightening down the road.
    """
    import http.server
    import socketserver
    import threading
    import zipfile
    from urllib.parse import unquote, urlsplit

    serve_dir_str = str(serve_dir)
    audio_bundle = serve_dir / "assets" / "audio_bundle.zip"

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a: object, **kw: object) -> None:
            super().__init__(*a, directory=serve_dir_str, **kw)

        def log_message(self, fmt: str, *args: object) -> None:
            # Silence the per-request stderr spam — pywebview's window already
            # logs the page URL on load.
            pass

        def _serve_bundled_audio(self, *, head_only: bool = False) -> bool:
            """Serve ``assets/audio/...`` from the build-time ZIP when frozen.

            Development runs keep normal loose files, so this path activates
            only when ``audio_bundle.zip`` exists. Basic byte-range support
            keeps HTML audio seeking and WebView2 media loading reliable.
            """
            request_path = unquote(urlsplit(self.path).path).lstrip("/")
            prefix = "assets/audio/"
            if not audio_bundle.is_file() or not request_path.startswith(prefix):
                return False
            if ".." in Path(request_path).parts:
                self.send_error(400, "invalid audio path")
                return True
            member = request_path.removeprefix("assets/")
            try:
                with zipfile.ZipFile(audio_bundle, "r") as zf:
                    payload = zf.read(member)
            except KeyError:
                self.send_error(404, "audio not found")
                return True
            except (OSError, zipfile.BadZipFile) as exc:
                log.warning("audio bundle read failed for %s: %s", member, exc)
                self.send_error(500, "audio bundle unavailable")
                return True

            total = len(payload)
            start, end = 0, max(0, total - 1)
            status = 200
            range_header = self.headers.get("Range", "")
            if range_header.startswith("bytes=") and total:
                try:
                    raw_start, raw_end = range_header[6:].split("-", 1)
                    start = int(raw_start) if raw_start else 0
                    end = int(raw_end) if raw_end else total - 1
                    start = max(0, min(start, total - 1))
                    end = max(start, min(end, total - 1))
                    status = 206
                except (TypeError, ValueError):
                    start, end, status = 0, total - 1, 200
            body = payload[start:end + 1]
            self.send_response(status)
            self.send_header("Content-Type", "audio/ogg")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            self.send_header("Content-Length", str(len(body)))
            if status == 206:
                self.send_header("Content-Range", f"bytes {start}-{end}/{total}")
            self.end_headers()
            if not head_only:
                self.wfile.write(body)
            return True

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            if not self._serve_bundled_audio():
                super().do_GET()

        def do_HEAD(self) -> None:  # noqa: N802 - stdlib handler API
            if not self._serve_bundled_audio(head_only=True):
                super().do_HEAD()

    # Subclass so we can flip allow_reuse_address — without this, a rapid
    # close-then-reopen of the exe can hit "address in use" if the OS picks
    # the same random port both times before TIME_WAIT clears.
    class _ReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = _ReuseTCPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(
        target=server.serve_forever,
        name="kca-http",
        daemon=True,
    )
    thread.start()
    return port


def _parse_headless_quit_secs() -> int:
    """Return KCA_HEADLESS_QUIT_SECS as a positive int, or 0 if unset/invalid.

    Used by CI smoke tests to launch the binary, prove it boots + renders, and
    self-close after N seconds without needing an interactive display session.
    """
    raw = os.environ.get("KCA_HEADLESS_QUIT_SECS", "").strip()
    if not raw:
        return 0
    try:
        secs = int(raw)
    except ValueError:
        log.warning("KCA_HEADLESS_QUIT_SECS=%r is not an integer; ignoring", raw)
        return 0
    return max(0, secs)


def _schedule_headless_close(window: "webview.Window", secs: int) -> None:
    """Background-thread function passed to webview.start().

    pywebview calls this after the GUI loop is up. We arm a Timer that asks the
    window to destroy itself N seconds later. window.destroy() is thread-safe
    in pywebview — it marshals to the GUI thread internally.
    """
    log.info("headless mode: scheduling auto-close in %ds", secs)
    _log_event("state", "headless.armed", {"secs": secs})

    def _close() -> None:
        log.info("headless: timer fired — closing window after %ds", secs)
        _log_event("state", "headless.firing", {"secs": secs})
        try:
            window.destroy()
        except Exception as exc:  # pragma: no cover — best-effort cleanup
            log.warning("window.destroy() failed: %s", exc)
            _log_event("failure", "headless.destroy", {"err": str(exc)})

    threading.Timer(secs, _close).start()


def main() -> None:
    base_dir = get_base_dir()
    html_path = base_dir / HTML_FILENAME

    if not html_path.is_file():
        log.error("Could not find %s at %s", HTML_FILENAME, html_path)
        sys.exit(1)

    port = _start_local_http_server(base_dir)
    url = f"http://127.0.0.1:{port}/{HTML_FILENAME}"
    log.info("local http server on port %d, loading %s", port, url)

    window = webview.create_window(
        APP_TITLE,
        url=url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        min_size=(MIN_WIDTH, MIN_HEIGHT),
        js_api=JSBridge(),
    )
    storage_path = str(get_webview_storage_path())
    log.info("webview storage_path=%s (private_mode=False)", storage_path)

    # Optional headless smoke-test: env var KCA_HEADLESS_QUIT_SECS=N causes
    # the window to close itself after N seconds. Used by the Pi GHA workflow
    # to prove the boot path works without a real display session.
    headless_secs = _parse_headless_quit_secs()
    start_func = (lambda: _schedule_headless_close(window, headless_secs)) if headless_secs > 0 else None

    # private_mode=False keeps localStorage across launches.
    # storage_path pins WebView2's user data folder so PyInstaller's _MEI churn
    # never points it at a stale temp directory.
    try:
        webview.start(start_func, private_mode=False, storage_path=storage_path)
    except TypeError:
        # Older pywebview that lacks one of these kwargs — fall back gracefully.
        log.warning("webview.start kwargs unsupported; trying minimal call")
        webview.start(start_func)


if __name__ == "__main__":
    main()
