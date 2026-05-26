"""Append a 3-problem 'Math Minute' to the end of every lesson.

For a 2nd-grade-entry kid who's behind (33rd %ile): start well below grade
level and build, spiral the basics, keep it read-aloud multiple-choice so the
reading load doesn't get in the way of the math.

Design:
  * 3 math questions appended to each lesson's questions[], ids math1..math3.
  * skipGate=true -> the engine renders them as read-aloud MCQ with no warm-up
    gate (Bytey reads the problem and every answer choice).
  * Difficulty tiers track the lesson number (1-60). Higher tiers still mix in
    lower-tier review (spiral) so fluency on the basics keeps getting practiced.
  * Answers are COMPUTED here, so they're always correct. Distractors are
    plausible near-misses (off-by-one/two) -- the mistakes a real kid makes --
    not silly jokes, because for math the near-miss is the teaching signal.
  * Prompts use words ("plus", "minus") not symbols so the TTS reads cleanly.

Deterministic (seeded per lesson) and idempotent (strips any prior math* Qs
before appending). Run: python scripts/add_math_minute.py
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"


def _hash(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def num_distractors(ans: int, rng: random.Random, k: int = 3) -> list[str]:
    """Plausible near-miss wrong answers for a numeric problem."""
    cands = [ans - 2, ans - 1, ans + 1, ans + 2, ans + 3, ans - 3, ans + 5]
    seen: list[int] = []
    for c in cands:
        if c >= 0 and c != ans and c not in seen:
            seen.append(c)
    rng.shuffle(seen)
    return [str(x) for x in seen[:k]]


# Each generator returns (prompt, correct_text, [wrong_texts]).
def g_add(rng, n):
    a = rng.randint(0, n); b = rng.randint(0, n - a)
    return f"What is {a} plus {b}?", str(a + b), num_distractors(a + b, rng)


def g_sub(rng, n):
    a = rng.randint(1, n); b = rng.randint(0, a)
    return f"What is {a} minus {b}?", str(a - b), num_distractors(a - b, rng)


def g_doubles(rng, mx):
    a = rng.randint(1, mx)
    return f"What is {a} plus {a}?", str(a + a), num_distractors(a + a, rng)


def g_counton(rng, n):
    a = rng.randint(1, n - 2); b = rng.randint(1, 3)
    return f"Start at {a} and count up {b}. Where do you land?", str(a + b), num_distractors(a + b, rng)


def g_missing(rng, n):
    c = rng.randint(2, n); a = rng.randint(1, c)
    return f"{a} plus what makes {c}?", str(c - a), num_distractors(c - a, rng)


def g_compare(rng, n):
    a = rng.randint(1, n); b = rng.randint(1, n)
    while b == a:
        b = rng.randint(1, n)
    bigger = max(a, b)
    return f"Which number is bigger: {a} or {b}?", str(bigger), [str(min(a, b))]


def g_compare_small(rng, n):
    a = rng.randint(1, n); b = rng.randint(1, n)
    while b == a:
        b = rng.randint(1, n)
    return f"Which number is smaller: {a} or {b}?", str(min(a, b)), [str(max(a, b))]


def g_skip(rng, step):
    start = rng.choice([0, step, step * 2])
    seq = [start + step * i for i in range(3)]
    nxt = seq[3 - 1] + step
    return f"Count by {step}s: {seq[0]}, {seq[1]}, {seq[2]}. What comes next?", str(nxt), num_distractors(nxt, rng)


def g_tens(rng, mx):
    t = rng.randint(1, mx)
    return f"How many tens are in {t * 10}?", str(t), num_distractors(t, rng)


def g_wordadd(rng, n):
    a = rng.randint(1, n - 1); b = rng.randint(1, n - a)
    things = rng.choice(["toy cars", "stickers", "blocks", "apples", "crayons", "marbles"])
    return f"You have {a} {things}. You get {b} more. How many now?", str(a + b), num_distractors(a + b, rng)


def g_wordsub(rng, n):
    a = rng.randint(2, n); b = rng.randint(1, a)
    thing, act = rng.choice([("birds", "fly away"), ("cookies", "are eaten"), ("balloons", "pop"), ("ducks", "swim off")])
    return f"There are {a} {thing}. {b} {act}. How many are left?", str(a - b), num_distractors(a - b, rng)


def g_2plus1(rng):
    tens = rng.randint(1, 4); ones = rng.randint(0, 4); add = rng.randint(1, 5)
    a = tens * 10 + ones
    while ones + add > 9:  # keep no-regroup so it stays gentle
        add = rng.randint(1, 9 - ones) if ones < 9 else 1
    return f"What is {a} plus {add}?", str(a + add), num_distractors(a + add, rng)


# Tier skill pools. Each entry is a zero-arg-ish callable taking rng.
def tier_pool(t):
    if t == 1:   # lessons 1-12 — well below grade level
        return [lambda r: g_add(r, 10), lambda r: g_sub(r, 10),
                lambda r: g_doubles(r, 5), lambda r: g_counton(r, 10),
                lambda r: g_compare(r, 10)]
    if t == 2:   # 13-24
        return [lambda r: g_add(r, 20), lambda r: g_sub(r, 20),
                lambda r: g_missing(r, 10), lambda r: g_compare(r, 20),
                lambda r: g_add(r, 10), lambda r: g_doubles(r, 8)]
    if t == 3:   # 25-36
        return [lambda r: g_skip(r, 2), lambda r: g_skip(r, 5), lambda r: g_skip(r, 10),
                lambda r: g_tens(r, 9), lambda r: g_add(r, 20), lambda r: g_sub(r, 20),
                lambda r: g_missing(r, 20)]
    if t == 4:   # 37-48
        return [lambda r: g_wordadd(r, 20), lambda r: g_wordsub(r, 20),
                lambda r: g_2plus1(r), lambda r: g_tens(r, 9),
                lambda r: g_compare(r, 20), lambda r: g_skip(r, 5)]
    return [      # 49-60 — full mixed review, slightly harder
        lambda r: g_wordadd(r, 20), lambda r: g_wordsub(r, 20),
        lambda r: g_2plus1(r), lambda r: g_doubles(r, 10),
        lambda r: g_skip(r, 10), lambda r: g_tens(r, 9),
        lambda r: g_compare_small(r, 20), lambda r: g_missing(r, 20),
    ]


def tier_for(lesson_num: int) -> int:
    return min(5, (lesson_num - 1) // 12 + 1)


def make_option(text: str, correct: bool) -> dict:
    return {"text": text, "correct": correct, "_audio": f"assets/audio/o/{_hash(text)}.ogg"}


def build_math_questions(stem: str, lesson_num: int) -> list[dict]:
    rng = random.Random(f"math-{lesson_num}")
    pool = tier_pool(tier_for(lesson_num))
    qs = []
    used_prompts: set[str] = set()
    gens = pool[:]
    rng.shuffle(gens)
    gi = 0
    for k in range(1, 4):
        # pick a generator, retry for a fresh prompt + clean distractors
        prompt = correct = None; wrongs = []
        for _ in range(30):
            gen = gens[gi % len(gens)]; gi += 1
            prompt, correct, wrongs = gen(rng)
            if prompt not in used_prompts and len(wrongs) >= 1 and correct not in wrongs:
                break
        used_prompts.add(prompt)
        opts = [make_option(correct, True)] + [make_option(w, False) for w in wrongs]
        rng.shuffle(opts)
        qs.append({
            "id": f"math{k}",
            "skipGate": True,
            "variations": [{
                "prompt": prompt,
                "_audio": f"assets/audio/q/{stem[:9]}_math{k}_v0.ogg",
                "options": opts,
            }],
        })
    return qs


def main() -> None:
    changed = 0
    for f in sorted(LESSONS_DIR.glob("lesson_*.json")):
        raw = f.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        data = json.loads(raw.decode("utf-8"))
        m = re.match(r"lesson_(\d+)_", f.stem)
        if not m:
            continue
        lesson_num = int(m.group(1))
        qs = data.get("questions") or []
        # idempotent: drop any prior math* questions, then append fresh
        qs = [q for q in qs if not str(q.get("id", "")).startswith("math")]
        qs.extend(build_math_questions(f.stem, lesson_num))
        data["questions"] = qs
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write(text.replace("\n", newline))
        changed += 1
    print(f"added Math Minute (3 problems) to {changed} lessons")


if __name__ == "__main__":
    main()
