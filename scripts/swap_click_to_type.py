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

# Three bands of typing words, interleaved so every lesson sees a mix:
#   GOOFY    — instant-laugh words a 7yo finds hilarious (low typing-skill bar)
#   GAMES    — brands he already plays + characters from those worlds
#   AI_DEV   — words he MUST be able to type to make video games with AI
#
# Order matters inside each band: easy → harder. Caller's deterministic counter
# walks WORDS so re-runs produce identical files.
GOOFY: list[str] = [
    "FART", "POOP", "DIRT", "MUD", "GUNK", "GOOP", "BUTT", "BURP", "TOOT",
    "SLIME", "STINK", "BARF", "GROSS", "YUCK", "SNOT", "WART", "OOZE",
]
GAMES: list[str] = [
    "MARIO", "LUIGI", "SONIC", "TAILS", "KIRBY", "ZELDA", "LINK", "PIKACHU",
    "POKEMON", "FORTNITE", "MINECRAFT", "CREEPER", "STEVE", "BOWSER",
    "YOSHI", "GOOMBA", "PEACH", "TOAD", "EEVEE", "MEWTWO", "CHARMANDER",
    "BULBASAUR", "SQUIRTLE", "ROBLOX", "AMONG", "GOOGLE",
]
AI_DEV: list[str] = [
    # game-loop verbs
    "RUN", "JUMP", "MOVE", "FIRE", "STOP", "WAIT", "LOOP",
    # game pieces
    "HERO", "BOSS", "COIN", "STAR", "FLAG", "DOOR", "KEY", "LIFE",
    "SCORE", "TIMER", "LEVEL", "WORLD", "SCENE", "MUSIC", "SOUND",
    # code + AI words he'll type to make games
    "CODE", "BOT", "AGENT", "PROMPT", "PLAN", "BUILD", "DEBUG", "TEST",
    "FIX", "SAVE", "SHARE", "PIXEL", "FRAME", "SPRITE", "INPUT", "EVENT",
    "PLAYER", "ASSET", "IDEA", "GAME", "MAKE", "MAGIC", "SMART",
    "ROBOT", "BRAIN", "POWER", "READY", "START", "CLAUDE", "GEMINI",
    "CURSOR", "PYTHON", "JAVASCRIPT",  # longer, but he should know them
]

# Interleave: GOOFY, GAMES, AI_DEV repeating — each lesson gate gets a different
# flavor so typing practice mixes laugh-words + game-words + dev-words on rotation.
_max = max(len(GOOFY), len(GAMES), len(AI_DEV))
_inter: list[str] = []
for i in range(_max):
    if i < len(GOOFY): _inter.append(GOOFY[i])
    if i < len(GAMES): _inter.append(GAMES[i])
    if i < len(AI_DEV): _inter.append(AI_DEV[i])
WORDS: list[str] = _inter


def make_type_payload(word: str) -> dict:
    """Build a `type-this-word` interaction payload for a given word."""
    word = word.upper().strip()
    return {
        "prompt": f"Type {word} and press Send to keep going!",
        "target_display": word,
        "targets": [word.lower()],
        "hint_wrong": f"Type the word {word} (any case is fine).",
    }


# Clean pool for first-impression lessons (L01-L04). No GOOFY (FART, POOP, etc.)
# so a parent / teacher / friend trying the app for the first time doesn't
# immediately see fart-jokes. Only GAMES + AI_DEV bands.
WORDS_CLEAN: list[str] = []
_max_clean = max(len(GAMES), len(AI_DEV))
for i in range(_max_clean):
    if i < len(GAMES):  WORDS_CLEAN.append(GAMES[i])
    if i < len(AI_DEV): WORDS_CLEAN.append(AI_DEV[i])


def _pool_for(lesson_id: int) -> list[str]:
    """L01-L04 use the clean pool; everyone else gets the full WORDS pool."""
    return WORDS_CLEAN if lesson_id <= 4 else WORDS


def swap_lesson(path: Path, counter: list[int]) -> int:
    """Walk a lesson's questions[] and:
      (a) convert any leftover `click-the-thing` gate → `type-this-word`, AND
      (b) refresh every existing `type-this-word` payload w/ a new word from
          the lesson's pool (clean pool for L01-04, full pool elsewhere).
    Both produce a deterministic walk: re-runs are idempotent (same input → same output).
    Returns count of payloads written.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    lesson_id = int(path.stem.split("_")[1])
    pool = _pool_for(lesson_id)
    questions = data.get("questions") or []
    swaps = 0
    for q in questions:
        interaction = q.get("interaction") or {}
        kind = interaction.get("type")
        if kind not in ("click-the-thing", "type-this-word"):
            continue
        word = pool[counter[0] % len(pool)]
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
    print(f"\nDONE -- {total} type-word payloads written across {len(files)} lessons")
    print(f"Word pool size: {len(WORDS)}")


if __name__ == "__main__":
    main()
