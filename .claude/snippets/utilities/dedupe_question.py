# From: scripts/dedupe_distractors.py:89
# Rewrite distractor text per-slot so no string repeats > max_repeats times.

def dedupe_question(q: dict, max_repeats: int) -> int:
    """Rewrite distractor text per-slot so no string repeats > max_repeats times.
    Strategy: build the unique pool, expand w/ stylistic variants if too small
    for the question's wrong-slot count, then walk variations and assign the
    next pool entry that hasn't yet exceeded the cap. Returns count of rewrites.
    """
    pool = _unique_distractors_in_question(q)
    if not pool:
        return 0
    # Count wrong slots so we know how big the pool needs to be.
    wrong_slots = sum(
        1 for v in (q.get("variations") or []) for o in (v.get("options") or [])
        if not o.get("correct")
    )
    # Need at least ceil(wrong_slots / max_repeats) unique distractors.
    needed = -(-wrong_slots // max(1, max_repeats))
    if len(pool) < needed:
        pool = _expand_pool(pool, needed)
    rotation = deque(pool)
    used: Counter[str] = Counter()
    rewrites = 0
    for v in q.get("variations") or []:
        for opt in v.get("options") or []:
            if opt.get("correct"):
                continue
            current = (opt.get("text") or "").strip()
            # Skip if current is already under cap
            if used[current] < max_repeats:
                used[current] += 1
                continue
            # Find next pool entry under cap; rotate the deque so we don't
            # always pick the same replacement
            picked = None
            for _ in range(len(rotation) * 2):
                cand = rotation[0]
                rotation.rotate(-1)
                if used[cand] < max_repeats:
                    picked = cand
                    break
            if picked is None:
                # Pool exhausted — cycle anyway, picking the least-used
                picked = min(pool, key=lambda s: used[s])
            opt["text"] = picked
            used[picked] += 1
            rewrites += 1
    return rewrites
