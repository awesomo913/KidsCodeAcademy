# From: scripts/expand_lessons_v3.py:2200

def _build_variation(frame: dict[str, Any], paraphrase: str, seed: dict[str, Any],
                     variation_idx: int, question_idx: int) -> dict[str, Any]:
    salt = (question_idx + 1) * 100 + variation_idx
    facts = seed["facts"]
    wrongs = seed["wrongs"]
    prompt = paraphrase + frame["prompt"].format(concept=seed["concept"])
    # Stride by 3 so qi/v cross-product doesn't collide within 10 variations
    if frame["pick_truth"]:
        correct_text = facts[(variation_idx + question_idx * 3) % len(facts)]
        wrong_texts = _pick_n(wrongs, 3, salt)
    else:
        correct_text = wrongs[(variation_idx + question_idx * 3) % len(wrongs)]
        wrong_texts = _pick_n(facts, 3, salt)
    options = [{"text": correct_text, "correct": True}]
    options.extend({"text": t, "correct": False} for t in wrong_texts)
    options = _shuffled(options, salt + 13)
    return {"prompt": prompt, "options": options}
