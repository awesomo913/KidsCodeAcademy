# From: scripts/preprocess_acronyms.py:67
# Replace each acronym match with its spelled-out form. Returns (new_text, hits).

def _spell(text: str) -> tuple[str, list[str]]:
    """Replace each acronym match with its spelled-out form. Returns (new_text, hits)."""
    hits: list[str] = []
    def sub(m: re.Match) -> str:
        a = m.group(1)
        hits.append(a)
        return ACRONYMS[a]
    new = ACRONYM_RE.sub(sub, text)
    return new, hits
