# From: scripts/diversify_gates.py:118
# Build a fresh interaction payload for `gate_type`. Returns None if the

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
