# From: scripts/piper_bake.py:49
# Synthesize `text` to `out_path` (WAV). Returns True on success.

def synth(text: str, out_path: Path, voice_path: Path = DEFAULT_VOICE) -> bool:
    """Synthesize `text` to `out_path` (WAV). Returns True on success."""
    if not text or not text.strip():
        return False
    voice = _get_voice(voice_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        voice.synthesize_wav(text, w)
    return True
