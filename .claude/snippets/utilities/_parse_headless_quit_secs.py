# From: app.py:470
# Return KCA_HEADLESS_QUIT_SECS as a positive int, or 0 if unset/invalid.

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
