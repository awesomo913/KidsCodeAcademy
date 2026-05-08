"""Replace low-quality / age-inappropriate distractor strings across all lessons.

Problems found in audit:
  - "lie about" / "lying" — teaches dishonesty as even a "wrong" option
  - "shame" — toxic framing for losing
  - "iambic pentameter" — vocabulary too advanced for a 7yo
  - "hide forever" / "hide from everyone" — contradicts sharing/community values
  - "breakfast" silly comparison — confusing food↔code metaphor
  - "taste like onions" — same food-as-code confusion
  - "dizziness" — implies game loops cause physical harm
  - "old wizards" — fantasy reference that doesn't connect to coding
  - "decoration" used metaphorically — kid takes literally

Each problematic string maps to a kid-friendly silly replacement that's
clearly absurd but doesn't accidentally teach a wrong concept or use jargon.
Run: python scripts/fix_question_quality.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"

# Direct string replacements (case-sensitive matching the JSON exactly).
# Replacement strings are silly-but-harmless and avoid jargon/toxic framing.
REPLACEMENTS = {
    # === Severity 1: actually problematic for kids ===
    # lying as strategy
    "Always lie about what you know — it adds spice.":
        "Spin in three circles before you ask anything.",
    "Lie about what happened to make it fun.":
        "Sing the bug a lullaby until it falls asleep.",
    # shame around losing
    "Losing teaches us nothing, just shame.":
        "Losing means a tiny pizza falls from the sky.",
    # iambic pentameter (vocabulary too advanced)
    "Helpers only obey questions in iambic pentameter.":
        "Helpers only listen if you whisper to a sock.",
    "Inputs must be sung in iambic pentameter.":
        "Inputs must be sung to a banana.",
    # anti-sharing framing
    "Hide your work from everyone forever.":
        "Bury your work under a giant pile of socks.",
    "Hide it from everyone forever.":
        "Wrap it in a hundred layers of tape.",
    # CS-jargon misuse ("private")
    "Players never see the result — it is private.":
        "Players never see the result — it floats away.",

    # === Severity 2: confusing metaphors ("decoration" taken literally) ===
    "Action does nothing — it is a decoration.":
        "Action does nothing — it just naps.",
    "Action gets shy and hides.":
        "Action puts on a tiny hat.",
    "Platforms are decorations only — fall through!":
        "Platforms are made of clouds — fall through!",
    "Floors are decoration only — pure show.":
        "Floors are made of jelly — wobble through!",
    "Hitboxes are decorations only — like wallpaper.":
        "Hitboxes are made of fog — you pass right through.",

    # === Severity 3: lazy template reuse (same joke 5+ times) ===
    "Loops are required by old wizards.":
        "Loops are required by the moon.",
    "Editors are required by old wizards.":
        "Editors are powered by sneeze sounds.",
    "Patterns are required by old wizards.":
        "Patterns are required by talking ducks.",
    "Reveals are required by old wizards.":
        "Reveals only happen on Mondays.",

    # === Severity 4: silly food-as-code (drop the food angle) ===
    "Result is the same as breakfast.":
        "Result is a tiny invisible robot.",
    "Because closed tools always taste like onions.":
        "Because closed tools only work on Tuesdays.",
    "Helpers eat sticky notes for breakfast.":
        "Helpers carry sticky notes in tiny backpacks.",
    "Skills must include a song about onions.":
        "Skills must include a tiny dance.",

    # physical-harm framing
    "Loops are bad in games — they cause dizziness.":
        "Loops are bad in games — they get sleepy.",

    # vague "tickle" word — confusing direction
    "If you tickle a perceptron it forgets its job.":
        "If you blow on a model it forgets its job.",
    "Long ones tickle the helper.":
        "Long ones make the helper sleepy.",
    "Sparks must be tickled to stay.":
        "Sparks must be cheered to stay.",

    # off-topic
    "Cursor is fluent in pirate.":
        "Cursor only works inside a pumpkin.",
}


def fix_file(path: Path) -> int:
    """Replace problematic strings (raw text, not json-escaped — the file stores
    em-dash etc. as literal Unicode chars, not \\u2014 escapes). Returns count.
    """
    text = path.read_text(encoding="utf-8")
    swaps = 0
    for bad, good in REPLACEMENTS.items():
        count = text.count(bad)
        if count:
            text = text.replace(bad, good)
            swaps += count
    if swaps:
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            print(f"FAIL {path.name}: replacement produced invalid JSON ({exc}) - skipping")
            return 0
        path.write_text(text, encoding="utf-8")
    return swaps


def main() -> None:
    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    total = 0
    for path in files:
        try:
            n = fix_file(path)
        except OSError as exc:
            print(f"FAIL {path.name}: {exc}")
            continue
        if n:
            print(f"  {path.name}: {n} replacements")
            total += n
    print(f"\nDONE - {total} bad-distractor replacements across {len(files)} lessons")
    print(f"Replacement rules: {len(REPLACEMENTS)}")


if __name__ == "__main__":
    main()
