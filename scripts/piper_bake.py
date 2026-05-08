"""Piper TTS bake helper.

Wraps Piper's Python API into one `synth(text, out_path)` call so the rest of
the bake pipeline doesn't care which engine is in use. Output is 22.05 kHz
mono WAV, compatible with the existing post-process stage in prebake_audio.py.

Voice file lives at `voices/en_US-amy-medium.onnx` (gitignored). Download with:
    python -m piper.download_voices en_US-amy-medium --download-dir voices

If the voice file is missing, `is_available()` returns False so callers can
fall back to pyttsx3.
"""
from __future__ import annotations

import logging
import wave
from pathlib import Path
from typing import Optional

log = logging.getLogger("piper-bake")

ROOT = Path(__file__).resolve().parent.parent
VOICES_DIR = ROOT / "voices"
DEFAULT_VOICE = VOICES_DIR / "en_US-amy-medium.onnx"

_voice_cache: Optional[object] = None


def is_available(voice_path: Path = DEFAULT_VOICE) -> bool:
    """True if Piper is importable AND the voice file exists."""
    if not voice_path.is_file():
        return False
    try:
        import piper  # noqa: F401
    except ImportError:
        return False
    return True


def _get_voice(voice_path: Path = DEFAULT_VOICE):
    global _voice_cache
    if _voice_cache is None:
        from piper import PiperVoice
        _voice_cache = PiperVoice.load(str(voice_path))
        log.info("loaded piper voice: %s", voice_path.name)
    return _voice_cache


def synth(text: str, out_path: Path, voice_path: Path = DEFAULT_VOICE) -> bool:
    """Synthesize `text` to `out_path` (WAV). Returns True on success."""
    if not text or not text.strip():
        return False
    voice = _get_voice(voice_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        voice.synthesize_wav(text, w)
    return True
