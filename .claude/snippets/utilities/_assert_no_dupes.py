# From: scripts/expand_lessons_v3.py:2219
# Fail loud if two variations share the same prompt OR same correct text.

def _assert_no_dupes(variations: list[dict[str, Any]], qid: str) -> None:
    """Fail loud if two variations share the same prompt OR same correct text."""
    seen_prompts = set()
    seen_correct = set()
    for v in variations:
        p = v.get("prompt", "")
        c_text = next((o["text"] for o in v.get("options", []) if o.get("correct")), "")
        if p in seen_prompts:
            raise ValueError(f"{qid}: duplicate prompt across variations: {p!r}")
        if c_text in seen_correct:
            raise ValueError(f"{qid}: duplicate correct-answer across variations: {c_text!r}")
        seen_prompts.add(p)
        seen_correct.add(c_text)
