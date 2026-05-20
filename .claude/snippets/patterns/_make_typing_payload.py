# From: scripts/purge_filler_gates.py:62

def _make_typing_payload(lesson_id: int, q_idx: int) -> dict:
    return {
        "prompt": "Type this word!",
        "word": _swap_word(lesson_id, q_idx),
    }
