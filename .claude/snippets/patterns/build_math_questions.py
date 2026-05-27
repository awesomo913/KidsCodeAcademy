# From: scripts/add_math_minute.py:155

def build_math_questions(stem: str, lesson_num: int) -> list[dict]:
    rng = random.Random(f"math-{lesson_num}")
    pool = tier_pool(tier_for(lesson_num))
    qs = []
    used_prompts: set[str] = set()
    gens = pool[:]
    rng.shuffle(gens)
    gi = 0
    for k in range(1, 4):
        # pick a generator, retry for a fresh prompt + clean distractors
        prompt = correct = None; wrongs = []
        for _ in range(30):
            gen = gens[gi % len(gens)]; gi += 1
            prompt, correct, wrongs = gen(rng)
            if prompt not in used_prompts and len(wrongs) >= 1 and correct not in wrongs:
                break
        used_prompts.add(prompt)
        opts = [make_option(correct, True)] + [make_option(w, False) for w in wrongs]
        rng.shuffle(opts)
        qs.append({
            "id": f"math{k}",
            "skipGate": True,
            "variations": [{
                "prompt": prompt,
                "_audio": f"assets/audio/q/{stem[:9]}_math{k}_v0.ogg",
                "options": opts,
            }],
        })
    return qs
