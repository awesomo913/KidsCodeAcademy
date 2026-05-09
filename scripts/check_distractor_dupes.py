"""Audit lesson questions for over-repeated wrong-answer (distractor) text.

If the SAME wrong-answer string appears in many variations of one question, the
kid pattern-matches: "I keep seeing 'pretty buttons' — that's the wrong one"
within 1 lesson visit. Defeats the entire anti-memorization point of having
multiple variations.

This script scans every lesson's `questions[].variations[].options[]`, counts
how often each wrong-answer text appears within the same question, and flags
any string that appears more than `--max-repeats` times (default 3).

Returns exit 1 on any flag — wired into `build.py` as a lint step so a future
content edit that re-introduces dupes blocks the build with a clear error.

Usage:
    python scripts/check_distractor_dupes.py             # exit 1 on flags
    python scripts/check_distractor_dupes.py --max-repeats 2
    python scripts/check_distractor_dupes.py --quiet     # only print failures
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("dupe-check")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--max-repeats", type=int, default=3,
                   help="max times a wrong-answer text can appear in one question (default 3)")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not files:
        log.error("no lessons found at %s", LESSONS_DIR)
        return 1

    flags: list[str] = []
    for lf in files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            flags.append(f"{lf.name}: invalid JSON ({exc})")
            continue
        for q_idx, q in enumerate(data.get("questions") or []):
            qid = q.get("id") or f"q{q_idx + 1}"
            wrong_counts: Counter[str] = Counter()
            for v in q.get("variations") or []:
                for opt in v.get("options") or []:
                    if not opt.get("correct"):
                        text = (opt.get("text") or "").strip()
                        if text:
                            wrong_counts[text] += 1
            for text, n in wrong_counts.most_common():
                if n > args.max_repeats:
                    flags.append(f"{lf.name} {qid}: '{text[:50]}' repeats {n}x (max {args.max_repeats})")

    if flags:
        if not args.quiet:
            print(f"\nDISTRACTOR-DUPE FLAGS ({len(flags)}):", file=sys.stderr)
        for f in flags:
            print(f"  {f}", file=sys.stderr)
        print(f"\n{len(flags)} dupe flag(s) — build BLOCKED. Vary the distractor text.",
              file=sys.stderr)
        return 1

    if not args.quiet:
        log.info("ALL CLEAN -- %d lessons scanned, no over-repeated distractors", len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
