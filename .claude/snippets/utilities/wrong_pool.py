# From: scripts/fix_duplicate_options.py:24
# All distinct wrong-option dicts used anywhere in this question.

def wrong_pool(question: dict) -> list[dict]:
    """All distinct wrong-option dicts used anywhere in this question."""
    seen: set[str] = set()
    pool: list[dict] = []
    for v in question.get("variations") or []:
        for o in v.get("options") or []:
            t = str(o.get("text") or "")
            if not o.get("correct") and t and t not in seen:
                seen.add(t)
                pool.append(o)
    return pool
