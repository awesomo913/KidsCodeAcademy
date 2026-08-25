"""Bake and compress only text changed by refine_flagged_questions.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "logs" / "refined_audio_manifest.json"


def main() -> int:
    if not MANIFEST.is_file():
        print(f"missing manifest: {MANIFEST}", file=sys.stderr)
        return 1
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compress_audio_ogg import _find_ffmpeg, convert_wav_to_ogg
    from piper_bake import is_available, synth

    if not is_available():
        print("Piper voice/runtime is unavailable", file=sys.stderr)
        return 1
    ffmpeg = _find_ffmpeg()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = dict(manifest.get("prompts", {}))
    items.update(manifest.get("options", {}))
    errors = 0
    for index, (rel, spoken_text) in enumerate(sorted(items.items()), 1):
        ogg = ROOT / rel
        wav = ogg.with_suffix(".wav")
        if not synth(str(spoken_text), wav) or not convert_wav_to_ogg(ffmpeg, wav, ogg):
            errors += 1
        if index % 25 == 0 or index == len(items):
            print(f"baked {index}/{len(items)}")
    print(f"targeted audio complete: {len(items) - errors} ok, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
