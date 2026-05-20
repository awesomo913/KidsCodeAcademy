# From: scripts/diversify_gates.py:110
# Pull a kid-safe word from the existing swap_click_to_type pool.

def _word_for(counter: int) -> str:
    """Pull a kid-safe word from the existing swap_click_to_type pool.
    Imports lazily to avoid hard dependency at module import."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from swap_click_to_type import WORDS, make_type_payload  # type: ignore
    return WORDS[counter % len(WORDS)]
