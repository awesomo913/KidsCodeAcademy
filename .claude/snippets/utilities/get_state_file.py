# From: app.py:81
# File-backed mirror of the kid's localStorage. Belt-and-suspenders persistence

def get_state_file() -> Path:
    """File-backed mirror of the kid's localStorage. Belt-and-suspenders persistence
    in case the WebView2 storage gets wiped (PyInstaller --onefile changes the
    _MEI temp path on every launch, which used to invalidate WebView2 storage).
    """
    return _appdata_root() / "state.json"
