# From: app.py:46
# Resolve resource base path for both dev and frozen (PyInstaller) modes.

def get_base_dir() -> Path:
    """Resolve resource base path for both dev and frozen (PyInstaller) modes."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent
