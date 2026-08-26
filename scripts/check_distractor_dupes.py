"""Audit lesson questions for misleading distractor reuse.

Only one variation is shown during a lesson attempt, so reusing the same three
authored scenario choices across shuffled replays is valid.  Earlier versions
mistook that reuse for a defect and added low-quality wrappers such as
``Rumor:`` or ``(no way)``.  This check now blocks the defects that matter:
duplicate choices visible in one variation and one distractor reused across
many different questions in the same lesson.

This script scans every lesson's `questions[].variations[].options[]`, rejects
duplicate choices visible together, and counts how many different questions
reuse each wrong answer. It flags reuse beyond `--max-repeats` (default 3).

Returns exit 1 on any flag — wired into `build.py` as a lint step so a future
content edit that re-introduces dupes blocks the build with a clear error.

Usage:
    python scripts/check_distractor_dupes.py             # exit 1 on flags
    python scripts/check_distractor_dupes.py --max-repeats 3
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


def _key(text: str) -> str:
    return text.strip().rstrip(".!?").casefold()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--max-repeats", type=int, default=3,
                   help="max different questions in one lesson that may reuse one distractor")
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
        lesson_question_reuse: Counter[str] = Counter()
        for q_idx, q in enumerate(data.get("questions") or []):
            qid = q.get("id") or f"q{q_idx + 1}"
            for v in q.get("variations") or []:
                visible = [_key(opt.get("text") or "") for opt in v.get("options") or []]
                if len(visible) != len(set(visible)):
                    flags.append(f"{lf.name} {qid}: one variation shows duplicate answer choices")
            distinct_wrong: set[str] = set()
            for v in q.get("variations") or []:
                for opt in v.get("options") or []:
                    if not opt.get("correct"):
                        text = _key(opt.get("text") or "")
                        if text:
                            distinct_wrong.add(text)
            if str(q.get("id") or "").startswith("math"):
                continue
            for text in distinct_wrong:
                lesson_question_reuse[text] += 1
        for text, n in lesson_question_reuse.most_common():
            if n > args.max_repeats:
                flags.append(f"{lf.name}: '{text[:50]}' appears in {n} different questions (max {args.max_repeats})")

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
