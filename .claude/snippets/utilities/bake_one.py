# From: scripts/bake_q7_audio.py:35
# Bake `text` to ROOT/ogg_rel. Returns 'baked' | 'skip' | 'fail'.

def bake_one(text: str, ogg_rel: str, ffmpeg: str, force: bool) -> str:
    """Bake `text` to ROOT/ogg_rel. Returns 'baked' | 'skip' | 'fail'."""
    ogg_path = ROOT / ogg_rel
    if ogg_path.exists() and not force:
        return "skip"
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        tmp = Path(tf.name)
    try:
        if not synth(text, tmp):
            return "fail"
        # Windows Defender can briefly lock a just-created output file, making
        # ffmpeg fail with "Invalid argument". Retry a few times with a short
        # backoff before giving up.
        for attempt in range(4):
            if convert_wav_to_ogg(ffmpeg, tmp, ogg_path):
                return "baked"
            time.sleep(0.4 * (attempt + 1))
        return "fail"
    finally:
        tmp.unlink(missing_ok=True)
