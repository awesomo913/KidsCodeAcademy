# From: build.py:109
# Phase 4: build a temp copy of `assets/` that EXCLUDES *.wav so PyInstaller

def _build_audio_pkg() -> Path | None:
    """Phase 4: build a temp copy of `assets/` that EXCLUDES *.wav so PyInstaller
    only bundles the smaller .ogg copies. Returns the temp pkg path or None on
    failure. Caller is responsible for cleanup via shutil.rmtree.
    """
    src = ROOT / "assets"
    if not src.is_dir():
        return None
    pkg_root = ROOT / "build_pkg"
    pkg = pkg_root / "assets"
    if pkg_root.exists():
        shutil.rmtree(pkg_root, ignore_errors=True)
    def _copy_no_wav(s, names):
        # Filter exposed to copytree to skip wavs — keeps the .ogg twins.
        return [n for n in names if n.lower().endswith(".wav")]
    try:
        shutil.copytree(src, pkg, ignore=_copy_no_wav)
    except OSError as exc:
        log.warning("could not stage audio pkg: %s", exc)
        return None
    return pkg_root
