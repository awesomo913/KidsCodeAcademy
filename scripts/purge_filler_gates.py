"""Purge filler MCQ gates → type-this-word everywhere they appear.

The diversifier (v0.7.13) flipped Q2+ gates to type-this-word but intentionally
skipped Q1 + the outer-lesson `game` field — those were treated as "deep
demonstrative interactions." Per kid feedback, that left 6 lessons showing
pick-the-pic at Q1 + a few tap-the-glow / sprite-poke instances too. This
script does the broader sweep.

Targets (filler gates — pure presentation MCQ wrappers):
    pick-the-pic, tap-the-glow, sprite-poke

Spared (deep lesson mechanics — keep these as they teach the actual concept):
    level-painter, idea-spark, prompt-grader, sprite-mover, guided-talk,
    sequence-the-steps, place-blocks, timeline-order, drag-to-match,
    click-the-thing, world-layers, input-trace, costume-swapper, live-hud,
    polish-row, cursor-mini, playtest-preview, share-card, game-capstone,
    riddle-room, mascot-mood, show-work

For each replaced gate, payload becomes `{"prompt": "Type this word!",
"word": <kid-friendly word from rotating pool>}` so type-this-word's handler
has a real word to demand. Pool stays goofy/relevant (BYTEY, ROBOT, CODE, etc.)
since L01-04 already use the clean pool via swap_click_to_type.

Usage:
    python scripts/purge_filler_gates.py           # idempotent rewrite
    python scripts/purge_filler_gates.py --dry-run # show changes only
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("purge-filler")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"

FILLER_TYPES: frozenset[str] = frozenset({
    "pick-the-pic",
    "tap-the-glow",
    "sprite-poke",
})

# Rotating typing pool. Index by (lesson_id, q_idx) so adjacent lessons differ.
# Pulled from existing swap_click_to_type / diversify_gates conventions —
# all caps, kid-typeable, theme-relevant.
WORD_POOL: tuple[str, ...] = (
    "BYTEY", "ROBOT", "CODE", "GAME", "HERO", "JUMP", "MOVE", "LEVEL",
    "PIXEL", "SCORE", "WIN", "PLAY", "BUILD", "MAKE", "TYPE", "TAP",
    "STAR", "FUN", "GO", "YES", "DASH", "BOSS", "QUEST", "SPRITE",
)


def _swap_word(lesson_id: int, q_idx: int) -> str:
    return WORD_POOL[(lesson_id * 3 + q_idx) % len(WORD_POOL)]


def _make_typing_payload(lesson_id: int, q_idx: int) -> dict:
    return {
        "prompt": "Type this word!",
        "word": _swap_word(lesson_id, q_idx),
    }


def process_lesson(path: Path, dry: bool) -> dict:
    """Return per-lesson stats: { q_swaps, game_swap, lesson_id }."""
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    lesson_id = int(data.get("id", 0))
    stats = {"id": lesson_id, "title": data.get("title", ""), "q_swaps": 0, "game_swap": None}

    # Question gates (Q1 + Q2+ — both swept this time)
    for q_idx, q in enumerate(data.get("questions", [])):
        gate = (q.get("interaction") or {}).get("type")
        if gate in FILLER_TYPES:
            q["interaction"] = {
                "type": "type-this-word",
                "payload": _make_typing_payload(lesson_id, q_idx),
            }
            stats["q_swaps"] += 1

    # Outer lesson `game` field — only swap if it's a filler type. Deep
    # interactions (level-painter, idea-spark, etc.) are the lesson's actual
    # mechanic and stay.
    game_type = (data.get("game") or {}).get("type")
    if game_type in FILLER_TYPES:
        data["game"] = {
            "type": "type-this-word",
            "payload": _make_typing_payload(lesson_id, 0),
        }
        stats["game_swap"] = game_type

    if (stats["q_swaps"] or stats["game_swap"]) and not dry:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return stats


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not files:
        log.error("no lessons found")
        return 1

    total_q = 0
    total_game = 0
    touched_lessons = 0
    for path in files:
        try:
            stats = process_lesson(path, dry=args.dry_run)
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("skip %s: %s", path.name, exc)
            continue
        if stats["q_swaps"] or stats["game_swap"]:
            touched_lessons += 1
            log.info("L%02d %r  Q-swaps=%d  game-swap=%s",
                     stats["id"], stats["title"][:40],
                     stats["q_swaps"], stats["game_swap"])
        total_q += stats["q_swaps"]
        total_game += 1 if stats["game_swap"] else 0

    verb = "WOULD WRITE" if args.dry_run else "WRITE"
    log.info("%s — %d lessons touched, %d Q-gates + %d outer games swapped to type-this-word",
             verb, touched_lessons, total_q, total_game)
    return 0


if __name__ == "__main__":
    sys.exit(main())
