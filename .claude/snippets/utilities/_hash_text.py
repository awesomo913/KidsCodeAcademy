# From: scripts/bake_option_audio.py:38
# Stable short hash for a text string. 10 hex chars = 1.1T distinct

def _hash_text(text: str) -> str:
    """Stable short hash for a text string. 10 hex chars = 1.1T distinct
    values, plenty for ~10k unique option strings."""
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]
