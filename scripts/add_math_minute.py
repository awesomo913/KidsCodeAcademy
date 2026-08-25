"""Append a 3-problem 'Math Minute' to the end of every lesson.

For a second grader: begin with Grade 2 foundations, cover the full Grade 2
year, then bridge gently into early Grade 3 ideas. Every problem carries a
plain-language strategy tip that the interface can reveal and read aloud.

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


def g_place_value(rng, max_tens=9):
    tens = rng.randint(1, max_tens); ones = rng.randint(0, 9)
    n = tens * 10 + ones
    ask_tens = rng.choice([True, False])
    if ask_tens:
        return f"In the number {n}, how many tens are there?", str(tens), num_distractors(tens, rng)
    return f"In the number {n}, how many ones are there?", str(ones), num_distractors(ones, rng)


def g_make_tens_ones(rng):
    tens = rng.randint(1, 9); ones = rng.randint(0, 9)
    n = tens * 10 + ones
    return f"What number has {tens} tens and {ones} ones?", str(n), num_distractors(n, rng)


def g_even_odd(rng):
    n = rng.randint(1, 30)
    correct = "even" if n % 2 == 0 else "odd"
    wrong = "odd" if correct == "even" else "even"
    return f"Is {n} even or odd?", correct, [wrong]


def g_time(rng, half_hours=True):
    hour = rng.randint(1, 12)
    half = half_hours and rng.choice([True, False])
    shown = f"{hour}:30" if half else f"{hour}:00"
    correct = f"half past {hour}" if half else f"{hour} o'clock"
    wrongs = [
        f"{hour} o'clock" if half else f"half past {hour}",
        f"half past {(hour % 12) + 1}",
        f"{(hour % 12) + 1} o'clock",
    ]
    return f"The clock says {shown}. Which answer tells the time?", correct, wrongs


def g_money(rng):
    pennies = rng.randint(1, 9)
    nickels = rng.randint(0, 3)
    dimes = rng.randint(0, 3)
    total = pennies + nickels * 5 + dimes * 10
    parts = []
    if dimes: parts.append(f"{dimes} dime{'s' if dimes != 1 else ''}")
    if nickels: parts.append(f"{nickels} nickel{'s' if nickels != 1 else ''}")
    parts.append(f"{pennies} penn{'ies' if pennies != 1 else 'y'}")
    return f"You have {', '.join(parts)}. How many cents is that?", f"{total} cents", [f"{x} cents" for x in num_distractors(total, rng)]


def g_shape_sides(rng):
    shapes = [("triangle", 3), ("square", 4), ("pentagon", 5), ("hexagon", 6)]
    shape, sides = rng.choice(shapes)
    return f"How many sides does a {shape} have?", str(sides), [str(x) for x in [2, 3, 4, 5, 6] if x != sides][:3]


def g_measure(rng):
    a = rng.randint(2, 12); b = rng.randint(1, 6)
    longer = a + b
    item = rng.choice(["ribbon", "pencil", "toy train", "paper strip"])
    return f"A {item} is {a} inches long. Another is {longer} inches. How many inches longer is the second one?", str(b), num_distractors(b, rng)


def g_fraction(rng):
    shape = rng.choice(["pizza", "sandwich", "paper circle", "chocolate bar"])
    parts = rng.choice([2, 4])
    correct = "one half" if parts == 2 else "one fourth"
    wrongs = [x for x in ["one whole", "one half", "one third", "one fourth"] if x != correct]
    return f"A {shape} is split into {parts} equal parts. What is one part called?", correct, wrongs


def g_equal(rng):
    a = rng.randint(1, 9); b = rng.randint(1, 9); total = a + b
    missing = rng.randint(1, total - 1)
    return f"Make both sides equal: {a} plus {b} equals {missing} plus what?", str(total - missing), num_distractors(total - missing, rng)


def g_groups(rng):
    groups = rng.randint(2, 5); each = rng.choice([2, 3, 4, 5])
    total = groups * each
    return f"There are {groups} bags with {each} blocks in each bag. How many blocks altogether?", str(total), num_distractors(total, rng)


def g_share(rng):
    kids = rng.randint(2, 5); each = rng.randint(2, 5); total = kids * each
    return f"Share {total} stickers equally among {kids} kids. How many stickers does each kid get?", str(each), num_distractors(each, rng)


def g_data(rng):
    red = rng.randint(2, 9); blue = rng.randint(2, 9)
    while blue == red:
        blue = rng.randint(2, 9)
    if rng.choice([True, False]):
        return f"A picture graph shows {red} red votes and {blue} blue votes. How many votes altogether?", str(red + blue), num_distractors(red + blue, rng)
    diff = abs(red - blue)
    return f"A picture graph shows {red} red votes and {blue} blue votes. How many more votes did the winner get?", str(diff), num_distractors(diff, rng)


def g_make_ten(rng):
    a = rng.randint(1, 9)
    ans = 10 - a
    return f"{a} plus what makes 10?", str(ans), num_distractors(ans, rng)


def g_add_100(rng, regroup=False):
    if regroup:
        while True:
            a = rng.randint(16, 69); b = rng.randint(14, 29)
            if a + b <= 99 and a % 10 + b % 10 >= 10:
                break
    else:
        while True:
            a = rng.randint(10, 69); b = rng.randint(10, 29)
            if a + b <= 99 and a % 10 + b % 10 < 10:
                break
    return f"What is {a} plus {b}?", str(a + b), num_distractors(a + b, rng)


def g_sub_100(rng, regroup=False):
    if regroup:
        while True:
            a = rng.randint(31, 99); b = rng.randint(12, a - 1)
            if a % 10 < b % 10:
                break
    else:
        while True:
            a = rng.randint(20, 99); b = rng.randint(10, a - 1)
            if a % 10 >= b % 10:
                break
    return f"What is {a} minus {b}?", str(a - b), num_distractors(a - b, rng)


def g_place_value_1000(rng):
    hundreds = rng.randint(1, 9); tens = rng.randint(0, 9); ones = rng.randint(0, 9)
    number = hundreds * 100 + tens * 10 + ones
    place, answer = rng.choice([
        ("hundreds", hundreds), ("tens", tens), ("ones", ones),
    ])
    return f"In {number}, which digit is in the {place} place?", str(answer), num_distractors(answer, rng)


def g_time_five(rng):
    hour = rng.randint(1, 11); minute = rng.choice(range(0, 50, 5)); add = rng.choice([5, 10])
    finish = minute + add
    shown = f"{hour}:{minute:02d}"
    correct = f"{hour}:{finish:02d}"
    wrong_minutes = sorted({max(0, finish - 5), min(55, finish + 5), min(55, finish + 10)} - {finish})
    wrongs = [f"{hour}:{m:02d}" for m in wrong_minutes]
    return f"It is {shown}. What time will it be in {add} minutes?", correct, wrongs


def g_money_change(rng):
    price = rng.choice(range(10, 50, 5)); change = 50 - price
    wrongs = [f"{x} cents" for x in num_distractors(change, rng)]
    return f"A toy costs {price} cents. You pay 50 cents. How much change?", f"{change} cents", wrongs


def g_two_step(rng):
    start = rng.randint(8, 30); added = rng.randint(3, 12); removed = rng.randint(2, min(10, start + added - 1))
    ans = start + added - removed
    return (f"You have {start} blocks, get {added} more, then give away {removed}. How many are left?",
            str(ans), num_distractors(ans, rng))


def g_array(rng):
    rows = rng.randint(2, 5); each = rng.choice([2, 3, 4, 5, 10]); total = rows * each
    return f"An array has {rows} rows of {each} dots. How many dots?", str(total), num_distractors(total, rng)


def g_divide_groups(rng):
    groups = rng.randint(2, 5); each = rng.randint(2, 5); total = groups * each
    return f"Put {total} counters into groups of {each}. How many groups?", str(groups), num_distractors(groups, rng)


def g_area(rng):
    rows = rng.randint(2, 6); columns = rng.randint(2, 6); area = rows * columns
    return (f"A rectangle has {rows} rows of {columns} square tiles. What is its area?",
            f"{area} square units", [f"{x} square units" for x in num_distractors(area, rng)])


def g_perimeter(rng):
    length = rng.randint(3, 9); width = rng.randint(2, 7); perimeter = 2 * (length + width)
    return (f"A rectangle is {length} units long and {width} units wide. What is its perimeter?",
            f"{perimeter} units", [f"{x} units" for x in num_distractors(perimeter, rng)])


def g_fraction_compare(rng):
    denominator = rng.choice([3, 4, 6, 8]); a, b = rng.sample(range(1, denominator), 2)
    bigger = max(a, b)
    correct = f"{bigger}/{denominator}"
    wrongs = [f"{min(a, b)}/{denominator}", "They are equal", f"1/{denominator}"]
    wrongs = list(dict.fromkeys(x for x in wrongs if x != correct))
    return f"Which fraction is greater: {a}/{denominator} or {b}/{denominator}?", correct, wrongs


def g_unit_fraction(rng):
    a, b = rng.sample([2, 3, 4, 6, 8], 2)
    correct = f"1/{min(a, b)}"
    wrong = f"1/{max(a, b)}"
    return f"Which piece is larger: 1/{a} or 1/{b}?", correct, [wrong, "They are equal"]


def g_round_ten(rng):
    number = rng.randint(11, 89)
    while number % 10 == 0:
        number = rng.randint(11, 89)
    answer = int((number + 5) // 10 * 10)
    wrongs = [str(x) for x in {number // 10 * 10, (number // 10 + 1) * 10, answer + 10, max(0, answer - 10)} if x != answer]
    return f"Round {number} to the nearest ten.", str(answer), wrongs[:3]


def g_add_1000_no_regroup(rng):
    while True:
        a = rng.randint(120, 679); b = rng.randint(110, 289)
        if a + b <= 999 and all(int(x) + int(y) < 10 for x, y in zip(f"{a:03d}", f"{b:03d}")):
            break
    return f"What is {a} plus {b}?", str(a + b), num_distractors(a + b, rng)


def g_sub_1000_no_regroup(rng):
    while True:
        a = rng.randint(321, 999); b = rng.randint(110, a - 1)
        if all(int(x) >= int(y) for x, y in zip(f"{a:03d}", f"{b:03d}")):
            break
    return f"What is {a} minus {b}?", str(a - b), num_distractors(a - b, rng)


MATH_TIPS = {
    "addition-within-20": "Start with the bigger number and count on. You can also make a ten first.",
    "subtraction-within-20": "Think: what number plus the smaller number makes the larger number?",
    "make-a-ten": "Ten is a friendly number. Count how many more are needed to reach 10.",
    "doubles": "A double means two equal groups. Add the same number twice.",
    "missing-addend": "Count up from the first number until you reach the total.",
    "compare-within-100": "Compare tens first. If the tens match, compare the ones.",
    "place-value-2-digit": "The left digit tells the tens; the right digit tells the ones.",
    "shape-sides": "Trace the straight edges one at a time and count each edge once.",
    "addition-within-100": "Add tens to tens and ones to ones.",
    "subtraction-within-100": "Subtract tens from tens and ones from ones.",
    "regrouping-addition": "Add the ones first. Ten ones can be regrouped as one ten.",
    "regrouping-subtraction": "If there are not enough ones, trade one ten for ten ones.",
    "even-and-odd": "An even number can be split into pairs with none left over.",
    "skip-count": "Look for the same amount being added each time.",
    "time": "Count minutes forward in jumps of five, then check the hour.",
    "money": "A dime is 10 cents, a nickel is 5, and a penny is 1. Add each value.",
    "money-change": "Change is what is left: amount paid minus the price.",
    "place-value-3-digit": "Read hundreds, tens, then ones. Each place is worth ten times the place to its right.",
    "word-problem": "Tell the story with numbers: more means add; left or fewer usually means subtract.",
    "two-step-word-problem": "Do one action at a time. Keep the first answer for the second step.",
    "measurement": "To find how much longer, subtract the shorter length from the longer length.",
    "equalities": "The equal sign means both sides have the same value.",
    "data": "Read the labels, then add for a total or subtract to compare.",
    "fractions": "Equal parts must be the same size. The bottom number tells how many equal parts.",
    "arrays": "Rows are equal groups. Add each row or multiply rows by dots in each row.",
    "fair-sharing": "Deal one to each group again and again until none are left.",
    "division-groups": "Repeatedly make equal groups of the given size, then count the groups.",
    "area": "Area counts square tiles inside a shape: rows times columns.",
    "perimeter": "Perimeter is the distance around. Add all four sides.",
    "fraction-compare": "With the same bottom number, the fraction with more pieces is greater.",
    "unit-fraction-compare": "When one whole is cut into more pieces, each piece is smaller.",
    "round-to-ten": "Look at the ones digit: 0–4 rounds down; 5–9 rounds up.",
    "three-digit-addition": "Line up hundreds, tens, and ones. Add one place at a time.",
    "three-digit-subtraction": "Line up each place, then subtract ones, tens, and hundreds.",
}


# Tier skill pools. Each entry is (skill label, callable taking rng). The skill
# label is stored in lesson JSON so audits can prove curriculum coverage instead
# of guessing from prompt text.
def tier_pool(t):
    if t == 1:   # lessons 1-12 — Grade 2 foundations
        return [("addition-within-20", lambda r: g_add(r, 20)),
                ("subtraction-within-20", lambda r: g_sub(r, 20)),
                ("make-a-ten", g_make_ten),
                ("doubles", lambda r: g_doubles(r, 5)),
                ("missing-addend", lambda r: g_missing(r, 20)),
                ("compare-within-100", lambda r: g_compare(r, 100)),
                ("place-value-2-digit", lambda r: g_place_value(r, 9)),
                ("shape-sides", g_shape_sides)]
    if t == 2:   # 13-24 — Grade 2 core
        return [("addition-within-100", lambda r: g_add_100(r, False)),
                ("subtraction-within-100", lambda r: g_sub_100(r, False)),
                ("place-value-2-digit", lambda r: g_place_value(r, 9)),
                ("compare-within-100", lambda r: g_compare(r, 100)),
                ("even-and-odd", g_even_odd),
                ("skip-count", lambda r: g_skip(r, 5)),
                ("skip-count", lambda r: g_skip(r, 10)),
                ("time", g_time),
                ("money", g_money)]
    if t == 3:   # 25-36 — complete Grade 2 practice
        return [("regrouping-addition", lambda r: g_add_100(r, True)),
                ("regrouping-subtraction", lambda r: g_sub_100(r, True)),
                ("place-value-3-digit", g_place_value_1000),
                ("time", g_time_five),
                ("money-change", g_money_change),
                ("word-problem", lambda r: g_wordadd(r, 100)),
                ("word-problem", lambda r: g_wordsub(r, 100)),
                ("measurement", g_measure),
                ("equalities", g_equal),
                ("data", g_data)]
    if t == 4:   # 37-48 — Grade 2 mastery and concept models
        return [("two-step-word-problem", g_two_step),
                ("arrays", g_array),
                ("fair-sharing", g_share),
                ("fractions", g_fraction),
                ("area", g_area),
                ("perimeter", g_perimeter),
                ("data", g_data),
                ("place-value-3-digit", g_place_value_1000),
                ("regrouping-addition", lambda r: g_add_100(r, True)),
                ("regrouping-subtraction", lambda r: g_sub_100(r, True))]
    return [      # 49-60 — early Grade 3 bridge, still concept-first
        ("arrays", g_array),
        ("division-groups", g_divide_groups),
        ("area", g_area),
        ("perimeter", g_perimeter),
        ("fraction-compare", g_fraction_compare),
        ("unit-fraction-compare", g_unit_fraction),
        ("round-to-ten", g_round_ten),
        ("three-digit-addition", g_add_1000_no_regroup),
        ("three-digit-subtraction", g_sub_1000_no_regroup),
        ("two-step-word-problem", g_two_step),
        ("money-change", g_money_change),
        ("time", g_time_five),
        ("fractions", g_fraction),
    ]


def tier_for(lesson_num: int) -> int:
    return min(5, (lesson_num - 1) // 12 + 1)


def level_for(tier: int) -> str:
    return {
        1: "Grade 2 foundation",
        2: "Grade 2 core",
        3: "Grade 2 practice",
        4: "Grade 2 mastery",
        5: "Early Grade 3 bridge",
    }[tier]


def make_option(text: str, correct: bool) -> dict:
    return {"text": text, "correct": correct, "_audio": f"assets/audio/o/{_hash(text)}.ogg"}


def build_math_questions(stem: str, lesson_num: int, global_prompts: set[str]) -> list[dict]:
    rng = random.Random(f"math-{lesson_num}")
    tier = tier_for(lesson_num)
    pool = tier_pool(tier)
    qs = []
    used_prompts: set[str] = set()
    # Rotate deterministically through each tier so every important skill is
    # guaranteed coverage rather than left to random chance.
    offset = ((lesson_num - 1) % 12) * 3
    for k in range(1, 4):
        # pick a generator, retry for a fresh prompt + clean distractors
        prompt = correct = None; wrongs = []; skill = "mixed-review"
        for attempt in range(120):
            skill, gen = pool[(offset + k - 1 + attempt) % len(pool)]
            prompt, correct, wrongs = gen(rng)
            if (prompt not in used_prompts and prompt not in global_prompts
                    and len(wrongs) >= 1 and correct not in wrongs):
                break
        used_prompts.add(prompt)
        global_prompts.add(prompt)
        opts = [make_option(correct, True)] + [make_option(w, False) for w in wrongs]
        rng.shuffle(opts)
        qs.append({
            "id": f"math{k}",
            "skipGate": True,
            "math_skill": skill,
            "math_level": level_for(tier),
            "math_tip": MATH_TIPS[skill],
            "math_tip_audio": f"assets/audio/o/{_hash(MATH_TIPS[skill])}.ogg",
            "variations": [{
                "prompt": prompt,
                "_audio": f"assets/audio/q/{stem[:9]}_math{k}_v0.ogg",
                "options": opts,
            }],
        })
    return qs


def main() -> None:
    changed = 0
    global_prompts: set[str] = set()
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
        qs.extend(build_math_questions(f.stem, lesson_num, global_prompts))
        data["questions"] = qs
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write(text.replace("\n", newline))
        changed += 1
    print(f"added Math Minute (3 problems) to {changed} lessons")


if __name__ == "__main__":
    main()
