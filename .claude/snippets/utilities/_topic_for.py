# From: scripts/rewrite_q_openers.py:41
# Strip leading articles + lower-case for natural insertion in the opener.

def _topic_for(title: str, fallback: str) -> str:
    """Strip leading articles + lower-case for natural insertion in the opener."""
    t = (title or fallback or "this lesson").strip()
    for prefix in ("The ", "A ", "An "):
        if t.startswith(prefix):
            t = t[len(prefix):]
            break
    return t
