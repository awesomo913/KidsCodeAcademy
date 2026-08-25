"""Rebalance any wrong-answer that appears more than 3x within a question.

check_distractor_dupes.py (a build gate) blocks if any distractor repeats >3x in
one question. When a slot must be swapped, we replace the *excess* occurrence
with the question's least-used distractor that isn't already in that variation --
keeping every distractor at <=3 while staying on-topic and reusing baked audio.

Idempotent, preserves line endings. Run: python scripts/rebalance_distractors.py
"""
from __future__ import annotations

import json
import logging
from collections import Counter
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("rebalance")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
MAX_REPEATS = 3
MAX_LESSON_REPEATS = 6


def wrong_pool(question: dict) -> list[dict]:
    seen: set[str] = set()
    pool: list[dict] = []
    for v in question.get("variations") or []:
        for o in v.get("options") or []:
            t = str(o.get("text") or "")
            if not o.get("correct") and t and t not in seen:
                seen.add(t)
                pool.append(o)
    return pool


def counts(question: dict) -> Counter:
    c: Counter = Counter()
    for v in question.get("variations") or []:
        for o in v.get("options") or []:
            if not o.get("correct"):
                c[str(o.get("text") or "")] += 1
    return c


def rebalance_question(q: dict) -> bool:
    pool = wrong_pool(q)
    changed = False
    # Repeatedly fix the most over-used distractor until all are <= MAX_REPEATS.
    for _ in range(200):
        c = counts(q)
        over = [(t, n) for t, n in c.items() if n > MAX_REPEATS]
        if not over:
            break
        text, _n = max(over, key=lambda kv: kv[1])
        # Find a variation that holds `text` and swap it for the least-used pool
        # option not already present there.
        swapped = False
        for v in q.get("variations") or []:
            opts = v.get("options") or []
            present = {str(o.get("text") or "") for o in opts}
            if text not in present:
                continue
            cur = counts(q)
            cand = sorted(
                (p for p in pool if str(p.get("text")) not in present),
                key=lambda p: cur[str(p.get("text"))],
            )
            cand = [p for p in cand if cur[str(p.get("text"))] < MAX_REPEATS]
            if not cand:
                continue
            repl = cand[0]
            for i, o in enumerate(opts):
                if str(o.get("text") or "") == text and not o.get("correct"):
                    new_opt = {"text": repl["text"], "correct": False}
                    if repl.get("_audio"):
                        new_opt["_audio"] = repl["_audio"]
                    opts[i] = new_opt
                    changed = swapped = True
                    break
            if swapped:
                break
        if not swapped:
            log.warning("could not rebalance %r (pool exhausted)", text[:40])
            break
    return changed


def lesson_wrong_counts(data: dict) -> Counter:
    """Count non-math distractors across a whole lesson.

    Math answer choices are intentionally reused small numbers, so they are
    excluded from this prose-quality pass.
    """
    c: Counter = Counter()
    for q in data.get("questions") or []:
        if str(q.get("id") or "").startswith("math"):
            continue
        for v in q.get("variations") or []:
            for o in v.get("options") or []:
                if not o.get("correct"):
                    text = str(o.get("text") or "")
                    if text:
                        c[text] += 1
    return c


def rebalance_lesson(data: dict) -> bool:
    """Cap repeated prose distractors across all questions in one lesson.

    Replacement text is borrowed only from that lesson and is rejected if it
    is ever a correct answer there. This keeps swaps on-topic while avoiding
    the memorization pattern of seeing the same silly wrong line 8-9 times.
    """
    correct_texts = {
        str(o.get("text") or "")
        for q in data.get("questions") or []
        for v in q.get("variations") or []
        for o in v.get("options") or []
        if o.get("correct")
    }
    pool_by_text: dict[str, dict] = {}
    for q in data.get("questions") or []:
        if str(q.get("id") or "").startswith("math"):
            continue
        for v in q.get("variations") or []:
            for o in v.get("options") or []:
                text = str(o.get("text") or "")
                if not o.get("correct") and text and text not in correct_texts:
                    pool_by_text.setdefault(text, o)

    changed = False
    for _ in range(600):
        cur = lesson_wrong_counts(data)
        over = [(text, n) for text, n in cur.items() if n > MAX_LESSON_REPEATS]
        if not over:
            break
        text, _n = max(over, key=lambda item: item[1])
        swapped = False
        for q in data.get("questions") or []:
            if str(q.get("id") or "").startswith("math"):
                continue
            for v in q.get("variations") or []:
                opts = v.get("options") or []
                present = {str(o.get("text") or "") for o in opts}
                if text not in present:
                    continue
                candidates = sorted(
                    (o for t, o in pool_by_text.items()
                     if t not in present and cur[t] < MAX_LESSON_REPEATS),
                    key=lambda o: cur[str(o.get("text") or "")],
                )
                if not candidates:
                    continue
                replacement = candidates[0]
                for i, o in enumerate(opts):
                    if not o.get("correct") and str(o.get("text") or "") == text:
                        new_opt = {"text": replacement["text"], "correct": False}
                        if replacement.get("_audio"):
                            new_opt["_audio"] = replacement["_audio"]
                        opts[i] = new_opt
                        changed = swapped = True
                        break
                if swapped:
                    break
            if swapped:
                break
        if not swapped:
            log.warning("could not lesson-rebalance %r (pool exhausted)", text[:40])
            break
    return changed


def main() -> None:
    files_changed = 0
    for f in sorted(LESSONS_DIR.glob("lesson_*.json")):
        raw = f.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        data = json.loads(raw.decode("utf-8"))
        changed = False
        for q in data.get("questions") or []:
            if rebalance_question(q):
                changed = True
        if rebalance_lesson(data):
            changed = True
        if changed:
            text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
            with open(f, "w", encoding="utf-8", newline="") as fh:
                fh.write(text.replace("\n", newline))
            files_changed += 1
            log.info("rebalanced %s", f.name)
    log.info("done: %d files", files_changed)


if __name__ == "__main__":
    main()
