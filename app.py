"""CC Kids Academy — sandboxed coding tutorial for ages 7+.

Loads the kid-themed tutorial HTML in a native pywebview window.
All AI helpers (Claude / Cursor / Gemini) are pre-scripted JSON — zero network.
Bundled into a single .exe with PyInstaller.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import webview

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("cc-kids-academy")

# Crash logger (Crash Logger Rule). Best-effort; never block app launch on import.
try:
    sys.path.insert(0, str(Path.home() / ".claude" / "scripts"))
    from crash_logger import install as _install_crash, log_event as _log_event  # type: ignore
    _PROJECT_ROOT = Path(__file__).resolve().parent
    _install_crash(project_root=_PROJECT_ROOT)
    _log_event("info", "app.boot", {"frozen": getattr(sys, "frozen", False)})
except Exception as _exc:  # pragma: no cover
    log.info("crash_logger not available: %s", _exc)

APP_TITLE = "CC Kids Academy"
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


def get_user_data_dir() -> Path:
    """Writable per-user folder for kid project saves (Lesson 16)."""
    appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    user_dir = Path(appdata) / "CC-Kids-Academy" / "kid_projects"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


class JSBridge:
    """JS-callable bridge for the kid_projects save flow."""

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


def main() -> None:
    base_dir = get_base_dir()
    html_path = base_dir / HTML_FILENAME

    if not html_path.is_file():
        log.error("Could not find %s at %s", HTML_FILENAME, html_path)
        sys.exit(1)

    file_url = f"file:///{str(html_path).replace(os.sep, '/')}"
    log.info("loading %s", file_url)

    webview.create_window(
        APP_TITLE,
        url=file_url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        min_size=(MIN_WIDTH, MIN_HEIGHT),
        js_api=JSBridge(),
    )
    webview.start()


if __name__ == "__main__":
    main()
