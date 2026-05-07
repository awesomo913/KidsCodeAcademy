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


class JSBridge:
    """JS-callable bridge.

    Exposes:
      - save_kid_project(name, data)   — Lesson 16 SVG saves
      - save_state(json_blob)          — mirror localStorage to state.json
      - load_state() -> str            — read state.json (empty if missing)
      - clear_state()                  — wipe state.json (Reset all progress)
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

    serve_dir_str = str(serve_dir)

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a: object, **kw: object) -> None:
            super().__init__(*a, directory=serve_dir_str, **kw)

        def log_message(self, fmt: str, *args: object) -> None:
            # Silence the per-request stderr spam — pywebview's window already
            # logs the page URL on load.
            pass

    server = socketserver.TCPServer(("127.0.0.1", 0), _Handler)
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
