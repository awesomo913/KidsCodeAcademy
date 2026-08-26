"""Audit every question/variation across all lessons for 7-year-old quality.

Read-only. Flags issues by category and writes a ranked report so fixes can be
data-driven instead of eyeballed. Categories:

  prompt_too_long      prompt is hard to read aloud (long for a 7yo)
  hard_word            a word too advanced / jargon without a gloss
  weak_vocabulary      a Word Power entry is missing a short, plain definition
  bare_option          an answer choice is too short/abstract to mean anything
                       (numeric Math Minute choices are intentionally short)
  all_silly_wrong      every wrong answer is absurd -> kid wins by elimination,
                       learns nothing (good quizzes need ONE plausible-but-wrong)
  template_opener      prompt uses a worn-out template phrase
  dupe_distractor      same wrong-answer text reused across many questions

Run: python scripts/audit_question_quality.py
"""
from __future__ import annotations

import json
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
REPORT = ROOT / "logs" / "question_quality_audit.md"

PROMPT_MAX = 95  # chars; longer is a mouthful for a 7yo read-aloud
HARD_WORD_MIN = 12  # letters; very long words are usually too advanced
VOCAB_MEANING_MAX = 95
VOCAB_MEANING_MIN_WORDS = 4
VOCAB_MEANING_MAX_WORDS = 18

# Jargon a 7yo won't know unless it's glossed in the same string.
JARGON = {
    "algorithm", "parameter", "iteration", "recursion", "variable",
    "function", "boolean", "syntax", "compiler", "database", "perceptron",
    "neural", "gradient", "tensor", "asynchronous", "concurrency",
    "abstraction", "encapsulation", "polymorphism", "deprecated",
}

COMMON_LONG_WORDS = {"everything", "something", "yourself"}

# Silly markers: if ALL wrong answers contain one, the question is too easy.
SILLY = re.compile(
    r"\b(allergic|broccoli|sandwich|squirrel|dragon|giggle|couch|banana|"
    r"pancakes?|butterfl|lamp|homework|sneaker|cookie|farm|oil|puppy|bees?|"
    r"fridge|lasagna|tuesdays?|storm|carrots?|dreams?|cry|cheese|moth|"
    r"breakfast|hat|goose|pizza|sock|sneeze|moon|lullaby|wizard|onion|"
    r"slipper|jelly|cloud|whistle|bark|egg|dance|spin|sing|tickle|burp|"
    r"unicorn|spaghetti|frog|candy|smell|melt|feelings?|lemon|shoe|teacup|"
    r"leaf pile|bow before|parade|wifi|tiny chefs?|weather report|curfew|"
    r"soprano|cello|goldfish|jealous|shelf space|jars?|sacred|odd hats?|"
    r"sniff|snacks?|riddles?|butterfl|loud enough|vowels?|yelling|tiny dog|"
    r"paid|shy compliments?|pictures? of your foot|mail your question|wall|"
    r"invisible ink|computer needs a nap|slap the laptop|peanut|hot air balloon|"
    r"tiny mice|one tiny book|gummy worms?|sip of water|magic stones?|pebbles|"
    r"using its tail|spinning in circles|logs? out forever|bank closings?|holidays?|"
    r"24 hours?|grocery list|in pencil|turns purple|only on weekdays|at midnight|"
    r"taxes|sad and damp|rot if|scare people|approved by a committee|"
    r"grandparent|afraid of them|required to make a sequel|disappears?|"
    r"stacked on top|butterfl|smells? the code|loaf of bread|refuse to load|"
    r"written sideways|earns? you .*stars?|bold is best|gets? shorter|"
    r"invisible until .* says hi|x turns into y|song without lyrics|yell .?math|"
    r"local models? can fly|helper cries|saturdays?|singing chef|sings? every change|"
    r"inhaling crayons|because shy|tiny hats?|blob files?|gets? dizzy|sit there doing nothing|"
    r"secret forever|helps? no one|grows? new keys|never work,? ever|metal trees|"
    r"mushy notes?|only emoji|boring on purpose|does something fun|bigger ideas? are always|"
    r"long stories with chapters|last part you build|flying horse|train on mars|"
    r"slowest helper|llama .* closet|frowns? at parents|invisible coins|"
    r"signatures? and a stamp|write a poem instead)\b",
    re.IGNORECASE,
)

TEMPLATE_OPENERS = [
    re.compile(r"^(quick!|hey friend|bytey wonders|tell me|wait wait wait|pop quiz|listen up|think about this|got a quick one|brain time)", re.IGNORECASE),
    re.compile(r"^pick the most .+-y", re.IGNORECASE),
    re.compile(r"^which one is true about", re.IGNORECASE),
    re.compile(r"^pick the (silliest|wrong)", re.IGNORECASE),
    re.compile(r"^one of these is silly", re.IGNORECASE),
    re.compile(r"\b(the silliest claim|pick the wrong one)\b", re.IGNORECASE),
]


def words(text: str) -> list[str]:
    # Treat a friendly compound such as "back-and-forth" as three familiar
    # words, not one 14-letter monster. Keep apostrophes inside contractions.
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text or "")


def audit() -> dict:
    findings: dict[str, list] = {
        "prompt_too_long": [],
        "hard_word": [],
        "weak_vocabulary": [],
        "bare_option": [],
        "all_silly_wrong": [],
        "template_opener": [],
        "invalid_answer_set": [],
        "missing_audio": [],
        "missing_math_support": [],
    }
    distractor_counts: Counter = Counter()
    math_prompt_counts: Counter = Counter()
    math_skills: Counter = Counter()
    totals = {"lessons": 0, "questions": 0, "variations": 0}

    for f in sorted(LESSONS_DIR.glob("lesson_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        vocabulary = data.get("vocabulary", [])
        declared_glossary_words = {
            token.lower()
            for entry in vocabulary
            for token in words(str(entry.get("word", "")))
        }
        glossary_words: set[str] = set()
        seen_vocabulary: set[str] = set()
        for vocab_index, entry in enumerate(vocabulary):
            word = str(entry.get("word") or "").strip()
            meaning = str(entry.get("meaning") or "").strip()
            key = word.casefold()
            meaning_words = words(meaning)
            reasons: list[str] = []
            if not word:
                reasons.append("missing word")
            if key in seen_vocabulary:
                reasons.append("duplicate word")
            seen_vocabulary.add(key)
            if not (VOCAB_MEANING_MIN_WORDS <= len(meaning_words) <= VOCAB_MEANING_MAX_WORDS):
                reasons.append(
                    f"definition must be {VOCAB_MEANING_MIN_WORDS}-{VOCAB_MEANING_MAX_WORDS} words"
                )
            if len(meaning) > VOCAB_MEANING_MAX:
                reasons.append(f"definition is longer than {VOCAB_MEANING_MAX} characters")
            hard_definition_words = [
                token for token in meaning_words
                if ((len(token) >= HARD_WORD_MIN or token.lower() in JARGON)
                    and token.lower() not in declared_glossary_words
                    and token.lower() not in COMMON_LONG_WORDS)
            ]
            if hard_definition_words:
                reasons.append("definition contains hard word: " + hard_definition_words[0])
            if reasons:
                findings["weak_vocabulary"].append(
                    (f"{f.name} vocabulary[{vocab_index}]", word or "(missing)", "; ".join(reasons))
                )
            else:
                glossary_words.update(token.lower() for token in words(word))

            vocab_audio = entry.get("_audio")
            if not vocab_audio or not (ROOT / str(vocab_audio)).is_file():
                findings["missing_audio"].append(
                    (f"{f.name} vocabulary[{vocab_index}]", vocab_audio or "(missing _audio field)")
                )
        totals["lessons"] += 1
        lid = f.name
        for q in data.get("questions", []):
            totals["questions"] += 1
            qid = q.get("id", "?")
            is_math = str(qid).startswith("math")
            if is_math:
                math_skills[str(q.get("math_skill") or "MISSING")] += 1
            for vi, v in enumerate(q.get("variations", [])):
                totals["variations"] += 1
                where = f"{lid} {qid} v{vi}"
                prompt = str(v.get("prompt") or "")
                opts = v.get("options") or []
                if is_math:
                    math_prompt_counts[prompt] += 1
                    if not q.get("math_level") or not q.get("math_tip") or not q.get("math_tip_audio"):
                        findings["missing_math_support"].append((where, q.get("math_skill")))

                correct_count = sum(1 for option in opts if option.get("correct"))
                option_texts = [str(option.get("text") or "").strip() for option in opts]
                valid_count = 2 <= len(opts) <= 4 if is_math else len(opts) == 4
                if not valid_count or correct_count != 1 or len(set(option_texts)) != len(option_texts) or any(not text for text in option_texts):
                    findings["invalid_answer_set"].append((where, len(opts), correct_count, option_texts))
                audio_refs = [v.get("_audio")]
                audio_refs.extend(option.get("_audio") for option in opts)
                if is_math:
                    audio_refs.append(q.get("math_tip_audio"))
                for rel in audio_refs:
                    if not rel or not (ROOT / str(rel)).is_file():
                        findings["missing_audio"].append((where, rel or "(missing _audio field)"))

                if len(prompt) > PROMPT_MAX:
                    findings["prompt_too_long"].append((where, len(prompt), prompt))

                for w in words(prompt) + [w for o in opts for w in words(str(o.get("text") or ""))]:
                    lw = w.lower()
                    if ((len(w) >= HARD_WORD_MIN or lw in JARGON)
                            and lw not in glossary_words
                            and lw not in COMMON_LONG_WORDS):
                        findings["hard_word"].append((where, w, prompt[:60]))
                        break

                wrong = [str(o.get("text") or "") for o in opts if not o.get("correct")]
                for ot in wrong:
                    if not is_math and len(words(ot)) <= 2:
                        findings["bare_option"].append((where, ot))
                # Count a distractor once per question rather than once per
                # replay variation. Repeating a scenario's three authored
                # choices across shuffled replays is honest reuse; artificial
                # wrappers such as "Rumor:" are not quality.
                if not is_math:
                    for ot in set(wrong):
                        distractor_counts[(lid, qid, ot)] += 1
                if wrong and all(SILLY.search(ot) for ot in wrong):
                    findings["all_silly_wrong"].append((where, prompt[:50], wrong))

                if not is_math:
                    for rx in TEMPLATE_OPENERS:
                        if rx.search(prompt):
                            findings["template_opener"].append((where, prompt[:70]))
                            break

    text_question_counts: Counter = Counter()
    for (_lid, _qid, text), _count in distractor_counts.items():
        text_question_counts[text] += 1
    dupes = [(t, c) for t, c in text_question_counts.most_common(40) if c >= 8]
    math_dupes = [(t, c) for t, c in math_prompt_counts.most_common() if c > 1]
    return {"findings": findings, "dupes": dupes, "totals": totals,
            "math_dupes": math_dupes, "math_skills": math_skills}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="exit 1 when any quality finding remains")
    args = parser.parse_args()
    res = audit()
    REPORT.parent.mkdir(exist_ok=True)
    lines = ["# Question Quality Audit", ""]
    t = res["totals"]
    lines.append(f"Scanned **{t['lessons']} lessons / {t['questions']} questions / {t['variations']} variations**.")
    lines.append("")
    for cat, items in res["findings"].items():
        lines.append(f"## {cat} — {len(items)} hits")
        for row in items[:25]:
            lines.append(f"- `{row[0]}` — {row[1:]}")
        if len(items) > 25:
            lines.append(f"- … and {len(items) - 25} more")
        lines.append("")
    lines.append(f"## dupe_distractor — {len(res['dupes'])} strings reused >=8x")
    for text, c in res["dupes"]:
        lines.append(f"- {c}x — {text!r}")
    lines.append("")
    lines.append(f"## math_duplicate_prompt — {len(res['math_dupes'])} exact repeats")
    for text, c in res["math_dupes"]:
        lines.append(f"- {c}x — {text!r}")
    lines.append("")
    lines.append("## math_skill_coverage")
    for skill, count in sorted(res["math_skills"].items()):
        lines.append(f"- {skill}: {count}")
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("=== AUDIT SUMMARY ===")
    print(f"lessons={t['lessons']} questions={t['questions']} variations={t['variations']}")
    for cat, items in res["findings"].items():
        print(f"  {cat:20s} {len(items)}")
    print(f"  {'dupe_distractor':20s} {len(res['dupes'])} strings reused >=8x")
    print(f"  {'math_duplicate_prompt':20s} {len(res['math_dupes'])}")
    print(f"  {'math_skill_categories':20s} {len(res['math_skills'])}")
    print(f"report -> {REPORT}")
    issue_count = sum(len(items) for items in res["findings"].values())
    issue_count += len(res["dupes"]) + len(res["math_dupes"])
    return 1 if args.check and issue_count else 0


if __name__ == "__main__":
    sys.exit(main())
