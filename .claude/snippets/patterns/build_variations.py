# From: scripts/author_scenario_q7.py:204

def build_variations(stem: str, lesson_num: str, prompt: str, correct: str, wrong: list[str]) -> list[dict]:
    base_opts = [_opt(correct, True)] + [_opt(w, False) for w in wrong]
    variations = []
    for i, opener in enumerate(OPENERS):
        opts = base_opts[:]
        random.Random(f"{stem}-{i}").shuffle(opts)
        variations.append({
            "prompt": opener + prompt,
            "_audio": f"assets/audio/q/{stem[:9]}_q7_v{i}.ogg",
            "options": opts,
        })
    return variations
