"""Bake audio for the rewritten q7 scenario questions only.

Targeted + non-destructive: it touches ONLY the q7 prompt files and any new
option files, leaving every other lesson's audio and JSON untouched. (The
general bake_option_audio.py flips all _audio paths to .wav first, which would
churn all 60 lessons -- we avoid that here.)

For each q7 variation:
  * prompt -> overwrite the variation's `_audio` ogg (text changed, must re-bake)
  * each option -> bake its hashed ogg if missing (reused texts already exist)

Synthesize to a temp WAV, encode to ogg/opus with the same settings as
compress_audio_ogg, delete the temp. Run: python scripts/bake_q7_audio.py
"""
from __future__ import annotations

import json
import logging
import sys
import tempfile
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("bake-q7")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from piper_bake import is_available, synth  # type: ignore  # noqa: E402
from compress_audio_ogg import _find_ffmpeg, convert_wav_to_ogg  # type: ignore  # noqa: E402


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


def main() -> int:
    if not is_available():
        log.error("Piper voice not available at voices/en_US-amy-medium.onnx")
        return 1
    ffmpeg = _find_ffmpeg()
    log.info("ffmpeg: %s", ffmpeg)

    counts = {"baked": 0, "skip": 0, "fail": 0}
    for f in sorted(LESSONS_DIR.glob("lesson_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        q7 = next((q for q in data.get("questions", []) if q.get("id") == "q7"), None)
        if not q7:
            continue
        for v in q7.get("variations", []):
            # prompt: always re-bake (text changed) -> force=True
            if v.get("_audio"):
                counts[bake_one(str(v.get("prompt") or ""), v["_audio"], ffmpeg, force=True)] += 1
            # options: bake only if the ogg is missing
            for o in v.get("options", []):
                if o.get("_audio"):
                    counts[bake_one(str(o.get("text") or ""), o["_audio"], ffmpeg, force=False)] += 1
    log.info("done: baked=%(baked)d skip=%(skip)d fail=%(fail)d", counts)
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
