"""Lift Q1 interactions for under-engaging arcs to themed mini-games.

The fun-review (2026-05-08) found two retention killers:
  - Arc H (L49-55): 7/7 lessons opened with type-this-word — kid is BUILDING
    a platformer but hits identical typing gates 7 lessons in a row.
  - Arcs B+C (L05-16): 12/12 lessons opened with passive `history-scene`
    (watch animation only) — long stretch of mostly-watch.

This script replaces Q1 of those 19 lessons with a topic-themed gate so the
kid does something authentic AND varied before answering questions.

Q2..Qn are NOT touched (they were already diversified separately).

Usage:
    python scripts/lift_q1_games.py            # idempotent rewrite
    python scripts/lift_q1_games.py --dry-run  # show changes only
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("lift-q1")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"

# Per-lesson Q1 lift map. Each value is the new `interaction` dict.
# Themed: the gate matches what the lesson is about so it feels purposeful.
Q1_LIFT: dict[int, dict] = {
    # === Arc B: AI History (was 6× passive history-scene) ===
    5: {
        "type": "timeline-order",
        "payload": {
            "prompt": "🧠 Math thinking happens in steps — put them in order!",
            "steps": ["See the problem", "Try a step", "Check your answer"],
        },
    },
    6: {
        "type": "drag-to-match",
        "payload": {
            "prompt": "🤖 Match the dreamer to the dream!",
            "pairs": [
                {"left": "Turing", "right": "🤖 Smart machine"},
                {"left": "A puzzle",  "right": "🧩 Hard problem"},
                {"left": "An idea",   "right": "💡 Imagination"},
            ],
        },
    },
    7: {
        "type": "pick-the-pic",
        "payload": {
            "prompt": "🦠 Tap the brain cell — the YES/NO part of an A I!",
            "choices": [
                {"glyph": "🧠", "right": True},
                {"glyph": "🍕", "right": False},
                {"glyph": "🚗", "right": False},
                {"glyph": "🎈", "right": False},
            ],
        },
    },
    8: {
        "type": "timeline-order",
        "payload": {
            "prompt": "🔁 Back-and-forth learning — what comes first?",
            "steps": ["You ask a question", "A I answers", "You correct it"],
        },
    },
    9: {
        "type": "tap-the-glow",
        "payload": {
            "prompt": "👀 Tap the word that gets ATTENTION!",
            "glyph": "✨",
        },
    },
    10: {
        "type": "timeline-order",
        "payload": {
            "prompt": "📚 How was the L L M born? Order the steps!",
            "steps": ["Read tons of books", "Learn word patterns", "Answer new questions"],
        },
    },
    # === Arc C: Helper Deep-Dives (was 6× history-scene + ToolSimulator chat hidden) ===
    11: {
        "type": "drag-to-match",
        "payload": {
            "prompt": "💜 Match Claude's superpowers!",
            "pairs": [
                {"left": "Claude",   "right": "💜 Long chat"},
                {"left": "Question", "right": "❓ You ask"},
                {"left": "Answer",   "right": "💬 Claude replies"},
            ],
        },
    },
    12: {
        "type": "tap-the-glow",
        "payload": {
            "prompt": "💻 Tap the cursor where Cursor types your code!",
            "glyph": "▮",
        },
    },
    13: {
        "type": "pick-the-pic",
        "payload": {
            "prompt": "🖼️ Gemini sees pictures! Tap the picture.",
            "choices": [
                {"glyph": "🖼️", "right": True},
                {"glyph": "📞", "right": False},
                {"glyph": "🧦", "right": False},
                {"glyph": "🥒", "right": False},
            ],
        },
    },
    14: {
        "type": "timeline-order",
        "payload": {
            "prompt": "⚙️ Codex finishes your code. What goes first?",
            "steps": ["You start typing", "Codex spots the pattern", "It finishes the line"],
        },
    },
    15: {
        "type": "drag-to-match",
        "payload": {
            "prompt": "🔓 OpenCode is OPEN! Match each piece.",
            "pairs": [
                {"left": "Code",    "right": "💻 Open"},
                {"left": "Friends", "right": "👫 Share"},
                {"left": "Learn",   "right": "📖 Read"},
            ],
        },
    },
    16: {
        "type": "pick-the-pic",
        "payload": {
            "prompt": "🦙 Ollama runs on YOUR computer — no internet! Tap the laptop.",
            "choices": [
                {"glyph": "💻", "right": True},
                {"glyph": "🌍", "right": False},
                {"glyph": "🛰️", "right": False},
                {"glyph": "📡", "right": False},
            ],
        },
    },
    # === Arc H: Iterative Build (was 7× type-this-word — biggest retention killer) ===
    49: {
        "type": "tap-the-glow",
        "payload": {
            "prompt": "🌟 Tap your wish-star to start your game!",
            "glyph": "🌟",
        },
    },
    50: {
        "type": "sprite-poke",
        "payload": {
            "prompt": "🦔 Tap the hero on the floor!",
            "glyph": "🦔",
        },
    },
    51: {
        "type": "tap-the-glow",
        "payload": {
            "prompt": "⬆️ Tap the JUMP button!",
            "glyph": "⬆️",
        },
    },
    52: {
        "type": "pick-the-pic",
        "payload": {
            "prompt": "🪙 Tap the COIN — that's what gives you score!",
            "choices": [
                {"glyph": "🪙", "right": True},
                {"glyph": "🦖", "right": False},
                {"glyph": "🥦", "right": False},
                {"glyph": "🪨", "right": False},
            ],
        },
    },
    53: {
        "type": "pick-the-pic",
        "payload": {
            "prompt": "👻 Tap the BAD GUY — the thing your hero must dodge!",
            "choices": [
                {"glyph": "👻", "right": True},
                {"glyph": "🦋", "right": False},
                {"glyph": "🌈", "right": False},
                {"glyph": "🍩", "right": False},
            ],
        },
    },
    54: {
        "type": "tap-the-glow",
        "payload": {
            "prompt": "⚡ Tap the POWER-UP to make your hero stronger!",
            "glyph": "⚡",
        },
    },
    55: {
        "type": "pick-the-pic",
        "payload": {
            "prompt": "🏁 Tap the FLAG — that's how you WIN!",
            "choices": [
                {"glyph": "🏁", "right": True},
                {"glyph": "🍕", "right": False},
                {"glyph": "🪣", "right": False},
                {"glyph": "🪥", "right": False},
            ],
        },
    },
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    rewritten = 0
    for lid, new_interaction in sorted(Q1_LIFT.items()):
        files = sorted(LESSONS_DIR.glob(f"lesson_{lid:02d}_*.json"))
        if not files:
            log.warning("L%02d: no lesson file found", lid)
            continue
        lf = files[0]
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.error("L%02d bad JSON: %s", lid, exc)
            continue
        questions = data.get("questions") or []
        if not questions:
            log.warning("L%02d: no questions[]", lid)
            continue
        old_type = (questions[0].get("interaction") or {}).get("type", "?")
        new_type = new_interaction["type"]
        if old_type == new_type and questions[0].get("interaction") == new_interaction:
            log.info("L%02d: already %s — skip", lid, new_type)
            continue
        questions[0]["interaction"] = new_interaction
        rewritten += 1
        log.info("L%02d: %s -> %s", lid, old_type, new_type)
        if not args.dry_run:
            lf.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    mode = "DRY-RUN" if args.dry_run else "WRITE"
    log.info("%s -- lifted Q1 in %d lessons", mode, rewritten)
    return 0


if __name__ == "__main__":
    sys.exit(main())
