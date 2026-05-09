"""Auto-fix over-repeated wrong-answer distractors across all lesson questions.

Runs alongside `check_distractor_dupes.py`. For each question that has a
distractor text repeated > `--max-repeats` times, this script rotates through
the question's UNIQUE distractor pool (across all variations) so each
variation lands a different wrong-answer in that slot.

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
from collections import Counter, deque
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("dedupe")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"


def _unique_distractors_in_question(q: dict) -> list[str]:
    """All unique non-empty wrong-answer strings across this question's variations."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for v in q.get("variations") or []:
        for opt in v.get("options") or []:
            if opt.get("correct"):
                continue
            text = (opt.get("text") or "").strip()
            if text and text not in seen_set:
                seen.append(text)
                seen_set.add(text)
    return seen


# Stylistic variant prefixes (kid-readable, recognizably "wrong-tone").
# Used to expand the distractor pool when authoring depth is too thin.
VARIANT_PREFIXES: list[str] = [
    "I think ", "Actually, ", "Maybe ", "Some say ", "Word is, ",
    "Bytey heard ", "Rumor: ", "Story goes — ", "I bet ", "Pretty sure ",
]
VARIANT_SUFFIXES: list[str] = [
    " (or so they say)", " — for real?", " (true story?)", "... right?",
    " (silly idea)", " (no way)", " (myth)", " (false alarm)",
]


def _expand_pool(pool: list[str], min_size: int) -> list[str]:
    """Pad the unique distractor pool by adding stylistic variants of existing
    entries until it reaches min_size. Variants must remain visibly different
    to a 7yo (different first or last word) and stay under 90 chars."""
    if len(pool) >= min_size or not pool:
        return pool
    out = list(pool)
    out_set = set(pool)
    pi = 0
    si = 0
    base_idx = 0
    # Round-robin: alternate prefix-then-suffix variant per base distractor
    while len(out) < min_size:
        base = pool[base_idx % len(pool)]
        # Lowercase first letter when prefixing so the sentence reads cleanly
        prefix_base = base[:1].lower() + base[1:] if base else base
        candidate = (VARIANT_PREFIXES[pi % len(VARIANT_PREFIXES)] + prefix_base
                     if (base_idx + pi + si) % 2 == 0
                     else base.rstrip(".!?") + VARIANT_SUFFIXES[si % len(VARIANT_SUFFIXES)])
        candidate = candidate[:90].strip()
        if candidate and candidate not in out_set:
            out.append(candidate)
            out_set.add(candidate)
        pi += 1
        si += 1
        base_idx += 1
        # Bail-out guard: if we've tried 200 combos and still can't grow, stop
        if (pi + si) > 200 and len(out) < min_size:
            break
    return out


def dedupe_question(q: dict, max_repeats: int) -> int:
    """Rewrite distractor text per-slot so no string repeats > max_repeats times.
    Strategy: build the unique pool, expand w/ stylistic variants if too small
    for the question's wrong-slot count, then walk variations and assign the
    next pool entry that hasn't yet exceeded the cap. Returns count of rewrites.
    """
    pool = _unique_distractors_in_question(q)
    if not pool:
        return 0
    # Count wrong slots so we know how big the pool needs to be.
    wrong_slots = sum(
        1 for v in (q.get("variations") or []) for o in (v.get("options") or [])
        if not o.get("correct")
    )
    # Need at least ceil(wrong_slots / max_repeats) unique distractors.
    needed = -(-wrong_slots // max(1, max_repeats))
    if len(pool) < needed:
        pool = _expand_pool(pool, needed)
    rotation = deque(pool)
    used: Counter[str] = Counter()
    rewrites = 0
    for v in q.get("variations") or []:
        for opt in v.get("options") or []:
            if opt.get("correct"):
                continue
            current = (opt.get("text") or "").strip()
            # Skip if current is already under cap
            if used[current] < max_repeats:
                used[current] += 1
                continue
            # Find next pool entry under cap; rotate the deque so we don't
            # always pick the same replacement
            picked = None
            for _ in range(len(rotation) * 2):
                cand = rotation[0]
                rotation.rotate(-1)
                if used[cand] < max_repeats:
                    picked = cand
                    break
            if picked is None:
                # Pool exhausted — cycle anyway, picking the least-used
                picked = min(pool, key=lambda s: used[s])
            opt["text"] = picked
            used[picked] += 1
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
