# From: scripts/expand_lessons_v3.py:2264
# Type-this-word gate template — every gate teaches typing across the curriculum.

def _gate(word: str) -> dict[str, Any]:
    """Type-this-word gate template — every gate teaches typing across the curriculum."""
    word = word.upper()
    return {
        "type": "type-this-word",
        "payload": {
            "prompt": f"Type {word} and press Send to keep going!",
            "target_display": word,
            "targets": [word.lower()],
            "hint_wrong": f"Type the word {word} (any case is fine).",
        },
    }
