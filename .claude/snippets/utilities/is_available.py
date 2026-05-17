# From: scripts/piper_bake.py:29
# True if Piper is importable AND the voice file exists.

def is_available(voice_path: Path = DEFAULT_VOICE) -> bool:
    """True if Piper is importable AND the voice file exists."""
    if not voice_path.is_file():
        return False
    try:
        import piper  # noqa: F401
    except ImportError:
        return False
    return True
