"""Bake one Piper TTS wav per question variation prompt.

For every lesson JSON in `lessons/`, walks `lesson.questions[*].variations[*]`,
synthesizes the prompt via Piper, writes a wav to
`assets/audio/q/lesson_<NN>_<qid>_v<idx>.wav`, and stores the relative path
back into the variation as a new `_audio` field.

Runtime (`index.html` QuestionFlow._renderAnswer) plays `<audio src=_audio>`
when present, falls back to Web Speech otherwise.

Usage:
    python scripts/bake_question_prompts.py            # incremental
    python scripts/bake_question_prompts.py --force    # re-bake everything

Idempotent: skips wavs whose file mtime is newer than the lesson JSON unless
`--force` is passed.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bake-q")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
OUT_DIR = ROOT / "assets" / "audio" / "q"


def _audio_relpath(num: str, qid: str, vidx: int) -> str:
    """Stable relative path used by both bake + runtime."""
    return f"assets/audio/q/lesson_{num}_{qid}_v{vidx}.wav"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true", help="re-bake every wav")
    p.add_argument("--limit", type=int, default=0, help="only bake first N lessons (debug)")
    args = p.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from piper_bake import is_available, synth  # type: ignore

    if not is_available():
        log.error("Piper not available. Place voice file at voices/en_US-amy-medium.onnx and pip install piper-tts.")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if args.limit:
        files = files[: args.limit]
    if not files:
        log.error("no lessons found")
        return 1

    total_baked = 0
    total_skipped = 0
    total_errors = 0
    for lf in files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.error("bad JSON in %s: %s", lf.name, exc)
            total_errors += 1
            continue
        num = lf.stem.split("_")[1]
        questions = data.get("questions") or []
        lesson_mtime = lf.stat().st_mtime
        changed = False
        for q in questions:
            qid = q.get("id") or "q?"
            vars_ = q.get("variations") or []
            for vidx, v in enumerate(vars_):
                prompt = (v.get("prompt") or "").strip()
                if not prompt:
                    continue
                rel = _audio_relpath(num, qid, vidx)
                out_path = ROOT / rel
                # Skip if already baked + lesson hasn't changed since
                if not args.force and out_path.is_file() and out_path.stat().st_mtime >= lesson_mtime:
                    if v.get("_audio") != rel:
                        v["_audio"] = rel
                        changed = True
                    total_skipped += 1
                    continue
                try:
                    ok = synth(prompt, out_path)
                except Exception as exc:  # noqa: BLE001
                    log.error("synth FAIL lesson_%s %s v%d: %s", num, qid, vidx, exc)
                    total_errors += 1
                    continue
                if ok:
                    v["_audio"] = rel
                    changed = True
                    total_baked += 1
        if changed:
            # Trailing newline keeps lesson JSONs in sync w/ diversify_gates.py +
            # bake_option_audio.py + swap_click_to_type.py — without it those
            # scripts mutually re-invalidate every run.
            lf.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            log.info("patched %s with %d audio paths", lf.name, sum(len(q.get("variations") or []) for q in questions))

    log.info("DONE -- baked=%d skipped=%d errors=%d", total_baked, total_skipped, total_errors)
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
