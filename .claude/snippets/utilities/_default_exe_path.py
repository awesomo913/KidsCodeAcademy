# From: scripts/verify_persistence.py:58
# Where build.py's publish step puts the binary, per platform.

def _default_exe_path() -> Path:
    """Where build.py's publish step puts the binary, per platform."""
    if os.name == "nt":
        return Path(r"C:/Users/computer/Desktop/AI/KidsCodeAcademy.exe")
    # Linux/macOS: build.py publishes to ~/Desktop or ~/ if no Desktop
    desktop = Path.home() / "Desktop"
    target_dir = desktop if desktop.is_dir() else Path.home()
    return target_dir / "KidsCodeAcademy"
