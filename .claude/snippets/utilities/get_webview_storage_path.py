# From: app.py:89
# Stable storage_path for pywebview's WebView2 user data folder.

def get_webview_storage_path() -> Path:
    """Stable storage_path for pywebview's WebView2 user data folder.
    Default pywebview private_mode=True wipes localStorage on close — we override
    it with a real persistent directory under %APPDATA%.
    """
    p = _appdata_root() / "webview_data"
    p.mkdir(parents=True, exist_ok=True)
    return p
