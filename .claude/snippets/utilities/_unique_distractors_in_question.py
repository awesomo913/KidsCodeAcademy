# From: scripts/dedupe_distractors.py:30
# All unique non-empty wrong-answer strings across this question's variations.

def _unique_distractors_in_question(q: dict) -> list[str]:
    """All unique non-empty wrong-answer strings across this question's variations."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for v in q.get("variations") or []:
        for opt in v.get("options") or []:
            if opt.get("correct"):
                continue
            text = (opt.get("text") or "").strip()
            if text and text not in seen_set:
                seen.append(text)
                seen_set.add(text)
    return seen
