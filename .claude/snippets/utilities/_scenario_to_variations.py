# From: scripts/expand_lessons_v3.py:2243
# Convert ONE hand-written scenario into VARIATIONS_PER_QUESTION variations.

def _scenario_to_variations(scenario: dict[str, Any], salt: int) -> list[dict[str, Any]]:
    """Convert ONE hand-written scenario into VARIATIONS_PER_QUESTION variations.

    Uses two layers:
      - layer 1 (v < 11): paraphrase prefix only (existing pattern)
      - layer 2 (v >= 11 OR fallback): SCENARIO_REFRAMES wrap the prompt itself
    Within 10 variations, cycle through both layers to ensure unique prompts.
    """
    out = []
    base = scenario["prompt"]
    for v in range(VARIATIONS_PER_QUESTION):
        if v < len(PARAPHRASES):
            prompt = PARAPHRASES[v] + base
        else:
            reframe = _SCENARIO_REFRAMES[(v - len(PARAPHRASES)) % len(_SCENARIO_REFRAMES)]
            prompt = reframe.format(p=base)
        opts = _shuffled(scenario["options"], salt + v * 17)
        out.append({"prompt": prompt, "options": [dict(o) for o in opts]})
    return out
