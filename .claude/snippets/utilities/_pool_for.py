# From: scripts/swap_click_to_type.py:81
# L01-L04 use the clean pool; everyone else gets the full WORDS pool.

def _pool_for(lesson_id: int) -> list[str]:
    """L01-L04 use the clean pool; everyone else gets the full WORDS pool."""
    return WORDS_CLEAN if lesson_id <= 4 else WORDS
