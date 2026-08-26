"""Repair duplicate answer choices without changing question meaning.

Only choices from replays with the exact same prompt may be borrowed. This is
important because one question family can contain both "pick the true fact"
and "pick the incorrect statement" replays; sharing answers across those two
prompt types can create several logically correct choices.

Idempotent: safe to re-run. Re-runs produce identical files.

Usage:
    python scripts/dedupe_distractors.py             # rewrite in place
    python scripts/dedupe_distractors.py --dry-run   # show changes only
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from copy import deepcopy
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("dedupe")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"


def dedupe_question(q: dict, max_repeats: int) -> int:
    """Replace only choices duplicated inside one visible variation."""
    del max_repeats  # kept in the CLI for compatibility with older workflows
    variations = q.get("variations") or []
    if not variations:
        return 0
    pools: dict[str, list[dict]] = {}
    for variation in variations:
        prompt = str(variation.get("prompt") or "")
        pool = pools.setdefault(prompt, [])
        known = {str(option.get("text") or "").strip().rstrip(".!?").casefold() for option in pool}
        for option in variation.get("options") or []:
            key = str(option.get("text") or "").strip().rstrip(".!?").casefold()
            if not option.get("correct") and key and key not in known:
                pool.append(deepcopy(option))
                known.add(key)
    rewrites = 0
    for variation in variations:
        options = variation.get("options") or []
        seen: set[str] = set()
        for index, option in enumerate(options):
            key = str(option.get("text") or "").strip().rstrip(".!?").casefold()
            if key not in seen:
                seen.add(key)
                continue
            if option.get("correct"):
                continue
            replacement = next((candidate for candidate in pools.get(str(variation.get("prompt") or ""), [])
                                if str(candidate.get("text") or "").strip().rstrip(".!?").casefold() not in seen), None)
            if replacement:
                options[index] = deepcopy(replacement)
                seen.add(str(replacement.get("text") or "").strip().rstrip(".!?").casefold())
                rewrites += 1
    return rewrites


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--max-repeats", type=int, default=3)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not files:
        log.error("no lessons")
        return 1

    total_rewrites = 0
    files_changed = 0
    for lf in files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.error("skip %s: %s", lf.name, exc)
            continue
        per_file = 0
        for q in data.get("questions") or []:
            per_file += dedupe_question(q, args.max_repeats)
        if per_file:
            total_rewrites += per_file
            files_changed += 1
            if not args.dry_run:
                lf.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )

    mode = "DRY-RUN" if args.dry_run else "WRITE"
    log.info("%s -- %d rewrites across %d files", mode, total_rewrites, files_changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
