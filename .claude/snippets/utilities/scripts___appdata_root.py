# From: scripts/verify_persistence.py:45
# Cross-platform per-user app data dir — mirrors app.py's _appdata_root().

def _appdata_root() -> Path:
    """Cross-platform per-user app data dir — mirrors app.py's _appdata_root()."""
    if os.name == "nt":  # Windows
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "KidsCodeAcademy"
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "KidsCodeAcademy"
    # Linux / Raspberry Pi
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else (Path.home() / ".local" / "share")
    return base / "KidsCodeAcademy"
