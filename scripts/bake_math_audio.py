"""Bake the complete Math Minute prompt set and any missing option audio."""
from __future__ import annotations

import json
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = ROOT / "lessons"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only-missing", action="store_true",
                        help="skip prompt clips that already exist")
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compress_audio_ogg import _find_ffmpeg, convert_wav_to_ogg
    from piper_bake import is_available, synth

    if not is_available():
        print("Piper voice/runtime is unavailable", file=sys.stderr)
        return 1
    ffmpeg = _find_ffmpeg()
    prompt_items: dict[str, str] = {}
    option_items: dict[str, str] = {}
    for lesson_file in sorted(LESSONS.glob("lesson_*.json")):
        data = json.loads(lesson_file.read_text(encoding="utf-8"))
        for question in data.get("questions", []):
            if not str(question.get("id", "")).startswith("math"):
                continue
            if question.get("math_tip") and question.get("math_tip_audio"):
                option_items[str(question["math_tip_audio"])] = str(question["math_tip"])
            for variation in question.get("variations", []):
                prompt_items[str(variation["_audio"])] = str(variation["prompt"])
                for option in variation.get("options", []):
                    option_items[str(option["_audio"])] = str(option["text"])

    errors = 0
    completed = 0
    prompt_total = sum(1 for rel in prompt_items if not args.only_missing or not (ROOT / rel).is_file())
    total = prompt_total + sum(1 for rel in option_items if not (ROOT / rel).is_file())
    for rel, spoken_text in sorted(prompt_items.items()):
        ogg = ROOT / rel
        if args.only_missing and ogg.is_file():
            continue
        wav = ogg.with_suffix(".wav")
        if not synth(spoken_text, wav) or not convert_wav_to_ogg(ffmpeg, wav, ogg):
            errors += 1
        completed += 1
        if completed % 25 == 0: print(f"baked {completed}/{total}")
    for rel, spoken_text in sorted(option_items.items()):
        ogg = ROOT / rel
        if ogg.is_file():
            continue
        wav = ogg.with_suffix(".wav")
        if not synth(spoken_text, wav) or not convert_wav_to_ogg(ffmpeg, wav, ogg):
            errors += 1
        completed += 1
        if completed % 25 == 0: print(f"baked {completed}/{total}")
    print(f"math audio complete: {completed - errors} ok, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
