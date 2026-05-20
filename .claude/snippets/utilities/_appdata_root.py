# From: app.py:53
# Stable per-user app data root.

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
