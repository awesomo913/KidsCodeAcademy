# From: scripts/expand_lessons_v2.py:1104
# One {prompt, options:[{text,correct}]*4} entry.

def _build_variation(
    frame: dict[str, Any],
    paraphrase: str,
    seed: dict[str, Any],
    variation_idx: int,
    question_idx: int,
) -> dict[str, Any]:
    """One {prompt, options:[{text,correct}]*4} entry."""
    salt = (question_idx + 1) * 100 + variation_idx
    facts = seed["facts"]
    wrongs = seed["wrongs"]
    prompt = paraphrase + frame["prompt"].format(concept=seed["concept"])

    if frame["pick_truth"]:
        correct_text = facts[(variation_idx + question_idx) % len(facts)]
        wrong_texts = _pick_n(wrongs, 3, salt)
    else:
        # spot_lie: correct = a WRONG fact (the silly one)
        correct_text = wrongs[(variation_idx + question_idx) % len(wrongs)]
        wrong_texts = _pick_n(facts, 3, salt)

    options = [{"text": correct_text, "correct": True}]
    options.extend({"text": t, "correct": False} for t in wrong_texts)
    options = _shuffled(options, salt + 7)
    return {"prompt": prompt, "options": options}
