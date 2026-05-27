# From: scripts/add_math_minute.py:37
# Plausible near-miss wrong answers for a numeric problem.

def num_distractors(ans: int, rng: random.Random, k: int = 3) -> list[str]:
    """Plausible near-miss wrong answers for a numeric problem."""
    cands = [ans - 2, ans - 1, ans + 1, ans + 2, ans + 3, ans - 3, ans + 5]
    seen: list[int] = []
    for c in cands:
        if c >= 0 and c != ans and c not in seen:
            seen.append(c)
    rng.shuffle(seen)
    return [str(x) for x in seen[:k]]
