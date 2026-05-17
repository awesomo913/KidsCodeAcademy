"""Diversify Q2+ gate interactions across all 60 lessons.

Before this script ran, Q2..Qn of every lesson was `type-this-word` — 330
identical gate types in a row. Kid sees the same "type the word" prompt over
and over.

This script rotates Q2+ across 6 gate types so every other gate is something
visibly different: a glowing tap, a picture-pick, a moving sprite to catch, a
3-step order puzzle, a drag-to-match, AND the existing typing.

It also gives the 12 `history-scene` lessons (L05-L16) a `timeline-order` gate
at Q2 themed to that lesson's content — so the previously passive "watch the
historical animation" lessons gain an authentic ordering interaction.

Q1 of every lesson is untouched (that's the deep lesson interaction).

Usage:
    python scripts/diversify_gates.py            # idempotent rewrite
    python scripts/diversify_gates.py --dry-run  # show changes only

Re-runs produce identical files (deterministic stride: id*7 + q_idx mod 6).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("diversify-gates")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"

# v0.7.13 — typing-only rotation per user direction. Multi-type rotation
# (tap-the-glow / pick-the-pic / sprite-poke / timeline-order / drag-to-match)
# was distracting + losing the typing practice the kid actually needs. The
# pools below are preserved for fast revert.
#
# To re-enable rotation: restore the multi-type list and re-run this script.
GATE_TYPES: list[str] = [
    "type-this-word",
]

# Sprite glyphs for sprite-poke — rotate so different lessons feel different
SPRITES: list[str] = ["🦔", "🐢", "🐰", "🦖", "🐱", "🐶", "🐸", "🤖", "👾", "🚀"]

# Glow glyphs for tap-the-glow
GLOW_GLYPHS: list[str] = ["⭐", "💎", "🍩", "🎮", "🍕", "🌈", "🦄", "⚡"]

# Pick-the-pic content pools — kid-relevant, kid-recognizable
PIC_POOLS: list[list[dict]] = [
    [{"glyph": "🎮", "right": True}, {"glyph": "🥦", "right": False},
     {"glyph": "📚", "right": False}, {"glyph": "🧦", "right": False}],
    [{"glyph": "🤖", "right": True}, {"glyph": "🐌", "right": False},
     {"glyph": "🥒", "right": False}, {"glyph": "🪨", "right": False}],
    [{"glyph": "🚀", "right": True}, {"glyph": "🥬", "right": False},
     {"glyph": "🧅", "right": False}, {"glyph": "🪣", "right": False}],
    [{"glyph": "⭐", "right": True}, {"glyph": "🌧️", "right": False},
     {"glyph": "🥒", "right": False}, {"glyph": "🪵", "right": False}],
    [{"glyph": "🍕", "right": True}, {"glyph": "🥦", "right": False},
     {"glyph": "🪨", "right": False}, {"glyph": "🧂", "right": False}],
]

# Drag-to-match pairs — short kid-friendly word pairs so the gate is fast
MATCH_POOLS: list[list[dict]] = [
    [{"left": "Mario", "right": "🍄"}, {"left": "Sonic", "right": "💨"},
     {"left": "Pokemon", "right": "⚡"}],
    [{"left": "Hero", "right": "🦸"}, {"left": "Code", "right": "💻"},
     {"left": "Game", "right": "🎮"}],
    [{"left": "Jump", "right": "⬆️"}, {"left": "Run", "right": "💨"},
     {"left": "Fire", "right": "🔥"}],
    [{"left": "Save", "right": "💾"}, {"left": "Share", "right": "📤"},
     {"left": "Build", "right": "🔨"}],
]

# Lesson-specific timeline-order steps for the 12 history-scene lessons (L05-L16).
# Each is a 3-step ordering that matches the lesson's actual subject.
# Picked by lesson number; falls back to a generic ordering if missing.
TIMELINE_BY_LESSON: dict[int, dict] = {
    5:  {"prompt": "Order the math thinking steps:",
         "steps": ["Look at the problem", "Try a step", "Check your answer"]},
    6:  {"prompt": "How did Turing dream up smart machines? Order it:",
         "steps": ["Notice a hard puzzle", "Imagine a machine that solves it", "Test the idea"]},
    7:  {"prompt": "Train your perceptron pet — what comes first?",
         "steps": ["Show it a picture", "Let it guess", "Tell it if it was right"]},
    8:  {"prompt": "Back-and-forth learning order:",
         "steps": ["You ask a question", "AI answers", "You correct it if it's wrong"]},
    9:  {"prompt": "How does AI pay attention to words?",
         "steps": ["See all the words", "Decide which ones matter", "Use those to answer"]},
    10: {"prompt": "How was an LLM born? Put it in order:",
         "steps": ["Read tons of books", "Learn word patterns", "Answer new questions"]},
    11: {"prompt": "What does Claude do first?",
         "steps": ["You type a question", "Claude thinks", "Claude writes back"]},
    12: {"prompt": "Cursor helps you code — order it:",
         "steps": ["You start typing", "Cursor sees your code", "Cursor suggests the rest"]},
    13: {"prompt": "Gemini handles pictures + words. Order:",
         "steps": ["Send a picture", "Ask a question about it", "Gemini answers"]},
    14: {"prompt": "Codex auto-completes code. Order:",
         "steps": ["You start typing", "Codex spots the pattern", "It finishes the line"]},
    15: {"prompt": "OpenCode is open for everyone. Order:",
         "steps": ["Open the chest", "Share with friends", "They can learn too"]},
    16: {"prompt": "Ollama runs on your computer — no internet. Order:",
         "steps": ["Download the model once", "Ask a question", "It answers without wifi"]},
}


def _word_for(counter: int) -> str:
    """Pull a kid-safe word from the existing swap_click_to_type pool.
    Imports lazily to avoid hard dependency at module import."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from swap_click_to_type import WORDS, make_type_payload  # type: ignore
    return WORDS[counter % len(WORDS)]


def _make_payload(gate_type: str, lesson_id: int, q_idx: int, word_counter: int) -> dict | None:
    """Build a fresh interaction payload for `gate_type`. Returns None if the
    gate type doesn't need rebuilding (e.g. when keeping existing type-this-word)."""
    if gate_type == "type-this-word":
        # Defer to swap_click_to_type's payload builder + use its per-lesson pool
        # so L01-04 stay clean (no GOOFY) and everyone else gets the full mix.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from swap_click_to_type import _pool_for, make_type_payload  # type: ignore
        pool = _pool_for(lesson_id)
        return make_type_payload(pool[word_counter % len(pool)])

    if gate_type == "tap-the-glow":
        return {
            "prompt": "Tap the glowing thing!",
            "glyph": GLOW_GLYPHS[(lesson_id + q_idx) % len(GLOW_GLYPHS)],
        }

    if gate_type == "pick-the-pic":
        pool_idx = (lesson_id * 3 + q_idx) % len(PIC_POOLS)
        return {
            "prompt": "Tap the right picture!",
            "choices": PIC_POOLS[pool_idx],
        }

    if gate_type == "sprite-poke":
        return {
            "prompt": "Tap the running hero!",
            "glyph": SPRITES[(lesson_id + q_idx) % len(SPRITES)],
        }

    if gate_type == "timeline-order":
        # Lesson-specific override for L05-L16; generic fallback otherwise.
        spec = TIMELINE_BY_LESSON.get(lesson_id) or {
            "prompt": "Put the steps in order:",
            "steps": ["First", "Next", "Last"],
        }
        return spec

    if gate_type == "drag-to-match":
        pool_idx = (lesson_id + q_idx) % len(MATCH_POOLS)
        return {
            "prompt": "Drag each one to its match!",
            "pairs": MATCH_POOLS[pool_idx],
        }

    return None


def diversify_lesson(path: Path, word_counter: list[int], dry: bool,
                     by_type: dict[str, int]) -> int:
    """Rewrite Q2..Qn interactions for one lesson. Q1 untouched.
    Updates `by_type` w/ what would be written (works in dry-run too).
    Returns count of gates rewritten."""
    data = json.loads(path.read_text(encoding="utf-8"))
    lesson_id = int(path.stem.split("_")[1])
    questions = data.get("questions") or []
    rewrites = 0
    for q_idx, q in enumerate(questions):
        if q_idx == 0:
            continue  # Q1 is the deep lesson interaction — leave it alone
        # Stride: id*7 + q_idx, mod 6 (coprime so adjacent lessons + adjacent
        # gates within a lesson differ).
        gate_idx = (lesson_id * 7 + q_idx) % len(GATE_TYPES)
        gate_type = GATE_TYPES[gate_idx]
        # v0.7.13 — history-scene timeline-order override disabled per user
        # direction (typing-only across the curriculum). Restore by un-commenting
        # if multi-type rotation returns.
        # if 5 <= lesson_id <= 16 and q_idx == 1:
        #     gate_type = "timeline-order"
        payload = _make_payload(gate_type, lesson_id, q_idx, word_counter[0])
        if gate_type == "type-this-word":
            word_counter[0] += 1
        if payload is None:
            continue
        q["interaction"] = {"type": gate_type, "payload": payload}
        rewrites += 1
        by_type[gate_type] = by_type.get(gate_type, 0) + 1
    if rewrites and not dry:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return rewrites


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not files:
        log.error("no lessons found")
        return 1

    word_counter = [0]
    total = 0
    by_type: dict[str, int] = {t: 0 for t in GATE_TYPES}
    for path in files:
        try:
            n = diversify_lesson(path, word_counter, args.dry_run, by_type)
        except (OSError, json.JSONDecodeError) as exc:
            log.error("FAIL %s: %s", path.name, exc)
            continue
        total += n

    mode = "DRY-RUN" if args.dry_run else "WRITE"
    log.info("%s — %d gates rewritten across %d lessons", mode, total, len(files))
    for t, c in by_type.items():
        log.info("  %-18s %d", t, c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
