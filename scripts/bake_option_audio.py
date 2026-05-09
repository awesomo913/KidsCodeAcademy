"""Bake one Piper TTS wav per UNIQUE answer-option text.

Walks every lesson's `variations[].options[]`, hashes each option's text,
and writes a single wav per unique hash to `assets/audio/o/<hash>.wav`.
Stores the relative path back into the option as `_audio`.

Many options repeat across paraphrases ("Yes!", "I love coding!"). Hashing
deduplicates them so we bake a few thousand unique strings instead of tens
of thousands of redundant copies.

Runtime (`index.html` startHoverAudio) plays this wav on hover. Falls back
to Web Speech if the wav is missing.

Usage:
    python scripts/bake_option_audio.py            # incremental
    python scripts/bake_option_audio.py --force    # re-bake everything
    python scripts/bake_option_audio.py --limit 5  # only first N lessons (debug)

Idempotent: skips wavs that already exist unless --force.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bake-opt")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
OUT_DIR = ROOT / "assets" / "audio" / "o"


def _hash_text(text: str) -> str:
    """Stable short hash for a text string. 10 hex chars = 1.1T distinct
    values, plenty for ~10k unique option strings."""
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def _audio_relpath(hsh: str) -> str:
    return f"assets/audio/o/{hsh}.wav"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from piper_bake import is_available, synth  # type: ignore

    if not is_available():
        log.error("Piper not available. Place voice file at voices/en_US-amy-medium.onnx and uv pip install piper-tts.")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if args.limit:
        files = files[: args.limit]
    if not files:
        log.error("no lessons found")
        return 1

    seen_hashes: set[str] = set()
    total_baked = 0
    total_skipped = 0
    total_errors = 0
    total_options = 0

    for lf in files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.error("bad JSON in %s: %s", lf.name, exc)
            total_errors += 1
            continue
        questions = data.get("questions") or []
        changed = False
        for q in questions:
            for v in q.get("variations") or []:
                for opt in v.get("options") or []:
                    text = (opt.get("text") or "").strip()
                    if not text:
                        continue
                    total_options += 1
                    hsh = _hash_text(text)
                    rel = _audio_relpath(hsh)
                    out_path = ROOT / rel
                    if opt.get("_audio") != rel:
                        opt["_audio"] = rel
                        changed = True
                    if hsh in seen_hashes:
                        total_skipped += 1
                        continue
                    seen_hashes.add(hsh)
                    if not args.force and out_path.is_file():
                        total_skipped += 1
                        continue
                    try:
                        ok = synth(text, out_path)
                    except (OSError, RuntimeError) as exc:
                        log.error("synth FAIL %r (hash=%s): %s", text[:40], hsh, exc)
                        total_errors += 1
                        continue
                    if ok:
                        total_baked += 1
        if changed:
            lf.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    log.info("DONE -- options=%d unique=%d baked=%d skipped=%d errors=%d",
             total_options, len(seen_hashes), total_baked, total_skipped, total_errors)
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
