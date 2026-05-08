"""Swap every `click-the-thing` gate interaction to `type-this-word`.

Pedagogy: every gate now teaches typing instead of just clicking.
Words rotate through a curated pool of 2-5 letter words appropriate for a 7yo.
Uses a deterministic counter per lesson so each gate gets a different word, and
the same input produces the same output on re-run (idempotent).

Run: python scripts/swap_click_to_type.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"

# Curated word pool — short, common, kid-typeable. Mixed lengths so each
# typing reps a different muscle memory. Order matters: easy first, harder later.
WORDS: list[str] = [
    # 2-letter (easiest)
    "GO", "OK", "ME", "US", "WE", "IT",
    # 3-letter (still easy)
    "YES", "FUN", "RUN", "BIG", "BOT", "WIN", "TOP", "SEE", "NEW", "USE",
    "GET", "PUT", "SET", "TRY", "ZIP", "AIM", "HOP", "DAY", "JOY", "RAD",
    # 4-letter
    "COOL", "NEXT", "PLAY", "GAME", "CODE", "JUMP", "STEP", "GOOD", "NICE",
    "OPEN", "HERO", "MAKE", "LOOK", "TYPE", "WORD", "MOVE", "TEAM", "SHIP",
    "SAVE", "READ", "WRITE", "HELP", "FAST",
    # 5-letter (slightly harder — practice once typing flows)
    "SUPER", "SMART", "READY", "BUILD", "START", "BLOCK", "BRAIN", "DREAM",
    "LEARN", "SOLVE", "PIXEL", "RIGHT", "SPACE", "POWER", "ROBOT", "LEVEL",
]


def make_type_payload(word: str) -> dict:
    """Build a `type-this-word` interaction payload for a given word."""
    word = word.upper().strip()
    return {
        "prompt": f"Type {word} and press Send to keep going!",
        "target_display": word,
        "targets": [word.lower()],
        "hint_wrong": f"Type the word {word} (any case is fine).",
    }


def swap_lesson(path: Path, counter: list[int]) -> int:
    """Walk a lesson's questions[] and convert click-the-thing → type-this-word.
    Returns count of swaps performed.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data.get("questions") or []
    swaps = 0
    for q in questions:
        interaction = q.get("interaction") or {}
        if interaction.get("type") != "click-the-thing":
            continue
        word = WORDS[counter[0] % len(WORDS)]
        counter[0] += 1
        q["interaction"] = {
            "type": "type-this-word",
            "payload": make_type_payload(word),
        }
        swaps += 1
    if swaps:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return swaps


def main() -> None:
    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    counter = [0]
    total = 0
    for path in files:
        try:
            n = swap_lesson(path, counter)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FAIL {path.name}: {exc}")
            continue
        if n:
            print(f"  {path.name}: {n} swaps")
            total += n
    print(f"\nDONE — {total} click-the-thing gates → type-this-word across {len(files)} lessons")
    print(f"Word pool size: {len(WORDS)}")


if __name__ == "__main__":
    main()
