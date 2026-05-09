"""Replace the flat 'What is <title>?' Q1-v0 prompt across all 60 lessons.

Before: every lesson's Q1 v0 reads "What is the perceptron pet?" — robotic and
school-quiz-flavored. Kid hits this opener ~10% of the time (random variation
pick) and 60 lessons of "What is X?" reads like school.

After: rotate v0 across 8 kid-friendly openers themed to the lesson topic.
Same goal text gets surrounded by varied energy: "🎮 Lightning round —", "🚀
Show me what you know about", "🤔 Bytey's brain teaser:" etc.

Only Q1-v0 of each lesson is touched. Q2-Qn variations already have rich
paraphrase prefixes (added 2026-05-08 in commit 1789993).

Usage: python scripts/rewrite_q_openers.py
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("rewrite-q0")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"

# 8 kid-friendly Q1-v0 openers. {topic} = lesson title with leading "the " stripped.
OPENERS: list[str] = [
    "🎮 Quick — show me what you know about {topic}!",
    "🚀 Bytey's first puzzle of the day: pick the TRUE one about {topic}!",
    "⭐ Lightning round! What do you remember about {topic}?",
    "🤔 Brain teaser — which one fits {topic}?",
    "🎯 Eyes on the prize! Pick the right answer about {topic}.",
    "🔥 Round one, FIGHT! Tap the best fact about {topic}.",
    "🦔 Bytey's pop quiz on {topic} — go!",
    "🧠 Power up your brain! Which one is right about {topic}?",
]


def _topic_for(title: str, fallback: str) -> str:
    """Strip leading articles + lower-case for natural insertion in the opener."""
    t = (title or fallback or "this lesson").strip()
    for prefix in ("The ", "A ", "An "):
        if t.startswith(prefix):
            t = t[len(prefix):]
            break
    return t


def main() -> int:
    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    rewritten = 0
    for lf in files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.error("bad JSON %s: %s", lf.name, exc)
            continue
        questions = data.get("questions") or []
        if not questions:
            continue
        q1 = questions[0]
        variations = q1.get("variations") or []
        if not variations:
            continue
        v0 = variations[0]
        topic = _topic_for(data.get("title", ""), data.get("goal", ""))
        # Stride across openers by lesson_id so adjacent lessons differ
        lesson_id = int(lf.stem.split("_")[1])
        opener = OPENERS[lesson_id % len(OPENERS)]
        new_prompt = opener.format(topic=topic)
        if v0.get("prompt") != new_prompt:
            v0["prompt"] = new_prompt
            rewritten += 1
            lf.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    log.info("DONE -- rewrote Q1-v0 prompt in %d lessons", rewritten)
    return 0


if __name__ == "__main__":
    main()
