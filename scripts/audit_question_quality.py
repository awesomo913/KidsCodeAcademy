"""Audit every question/variation across all lessons for 7-year-old quality.

Read-only. Flags issues by category and writes a ranked report so fixes can be
data-driven instead of eyeballed. Categories:

  prompt_too_long      prompt is hard to read aloud (long for a 7yo)
  hard_word            a word too advanced / jargon without a gloss
  bare_option          an answer choice is too short/abstract to mean anything
  all_silly_wrong      every wrong answer is absurd -> kid wins by elimination,
                       learns nothing (good quizzes need ONE plausible-but-wrong)
  template_opener      prompt uses a worn-out template phrase
  dupe_distractor      same wrong-answer text reused across many questions

Run: python scripts/audit_question_quality.py
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
REPORT = ROOT / "logs" / "question_quality_audit.md"

PROMPT_MAX = 95  # chars; longer is a mouthful for a 7yo read-aloud
HARD_WORD_MIN = 12  # letters; very long words are usually too advanced

# Jargon a 7yo won't know unless it's glossed in the same string.
JARGON = {
    "algorithm", "parameter", "iteration", "recursion", "variable",
    "function", "boolean", "syntax", "compiler", "database", "perceptron",
    "neural", "gradient", "tensor", "asynchronous", "concurrency",
    "abstraction", "encapsulation", "polymorphism", "deprecated",
}

# Silly markers: if ALL wrong answers contain one, the question is too easy.
SILLY = re.compile(
    r"\b(banana|sock|socks|sneeze|moon|pizza|lullaby|wizard|onion|slipper|"
    r"jelly|cloud|whistle|bark|egg|hat|dance|spin|sing|tickle|burp|"
    r"unicorn|dragon|spaghetti)\b",
    re.IGNORECASE,
)

TEMPLATE_OPENERS = [
    re.compile(r"^pick the most .+-y", re.IGNORECASE),
    re.compile(r"^which one is true about", re.IGNORECASE),
    re.compile(r"^pick the (silliest|wrong)", re.IGNORECASE),
    re.compile(r"^what is\b", re.IGNORECASE),
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'-]*", text or "")


def audit() -> dict:
    findings: dict[str, list] = {
        "prompt_too_long": [],
        "hard_word": [],
        "bare_option": [],
        "all_silly_wrong": [],
        "template_opener": [],
    }
    distractor_counts: Counter = Counter()
    totals = {"lessons": 0, "questions": 0, "variations": 0}

    for f in sorted(LESSONS_DIR.glob("lesson_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        totals["lessons"] += 1
        lid = f.name
        for q in data.get("questions", []):
            totals["questions"] += 1
            qid = q.get("id", "?")
            for vi, v in enumerate(q.get("variations", [])):
                totals["variations"] += 1
                where = f"{lid} {qid} v{vi}"
                prompt = str(v.get("prompt") or "")
                opts = v.get("options") or []

                if len(prompt) > PROMPT_MAX:
                    findings["prompt_too_long"].append((where, len(prompt), prompt))

                for w in words(prompt) + [w for o in opts for w in words(str(o.get("text") or ""))]:
                    lw = w.lower()
                    if (len(w) >= HARD_WORD_MIN or lw in JARGON) and lw not in {"everything", "something", "yourself"}:
                        findings["hard_word"].append((where, w, prompt[:60]))
                        break

                wrong = [str(o.get("text") or "") for o in opts if not o.get("correct")]
                for ot in wrong:
                    if len(words(ot)) <= 2:
                        findings["bare_option"].append((where, ot))
                    distractor_counts[ot] += 1
                if wrong and all(SILLY.search(ot) for ot in wrong):
                    findings["all_silly_wrong"].append((where, prompt[:50], wrong))

                for rx in TEMPLATE_OPENERS:
                    if rx.search(prompt):
                        findings["template_opener"].append((where, prompt[:70]))
                        break

    dupes = [(t, c) for t, c in distractor_counts.most_common(40) if c >= 8]
    return {"findings": findings, "dupes": dupes, "totals": totals}


def main() -> None:
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
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("=== AUDIT SUMMARY ===")
    print(f"lessons={t['lessons']} questions={t['questions']} variations={t['variations']}")
    for cat, items in res["findings"].items():
        print(f"  {cat:20s} {len(items)}")
    print(f"  {'dupe_distractor':20s} {len(res['dupes'])} strings reused >=8x")
    print(f"report -> {REPORT}")


if __name__ == "__main__":
    main()
