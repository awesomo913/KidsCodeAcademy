"""Bake vocabulary-guide and any newly referenced prompt/option audio."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "logs" / "vocabulary_audio_manifest.json"


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compress_audio_ogg import _find_ffmpeg, convert_wav_to_ogg
    from piper_bake import is_available, synth

    if not is_available():
        print("Piper runtime is unavailable", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    prompt_items = manifest.get("prompts", {})
    option_items = manifest.get("options", {})

    # The refinement script is intentionally safe to rerun and rewrites its
    # small manifest each time. Scan the finished curriculum too, so an earlier
    # run can never leave a newly referenced vocabulary or answer clip missing.
    for lesson_path in sorted((ROOT / "lessons").glob("lesson_*.json")):
        lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
        for guide in lesson.get("vocabulary", []):
            rel = guide.get("audio")
            if rel:
                option_items.setdefault(rel, f"{guide['word']}. {guide['meaning']}")
        for question in lesson.get("questions", []):
            for variant in question.get("variations", []):
                for option in variant.get("options", []):
                    rel = option.get("_audio")
                    if rel:
                        option_items.setdefault(rel, option.get("text", ""))
    ffmpeg = _find_ffmpeg()
    errors = 0
    work = [(rel, spoken, True) for rel, spoken in sorted(prompt_items.items())]
    work.extend((rel, spoken, False) for rel, spoken in sorted(option_items.items()))
    for index, (rel, spoken, force) in enumerate(work, 1):
        ogg = ROOT / rel
        if ogg.is_file() and not force:
            continue
        wav = ogg.with_suffix(".wav")
        if not synth(str(spoken), wav) or not convert_wav_to_ogg(ffmpeg, wav, ogg):
            errors += 1
        if index % 20 == 0 or index == len(work): print(f"checked {index}/{len(work)}")
    print(f"vocabulary audio checked: {len(work) - errors} ok, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
