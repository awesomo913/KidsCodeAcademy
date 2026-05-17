# From: scripts/swap_click_to_type.py:60
# Build a `type-this-word` interaction payload for a given word.

def make_type_payload(word: str) -> dict:
    """Build a `type-this-word` interaction payload for a given word."""
    word = word.upper().strip()
    return {
        "prompt": f"Type {word} and press Send to keep going!",
        "target_display": word,
        "targets": [word.lower()],
        "hint_wrong": f"Type the word {word} (any case is fine).",
    }
