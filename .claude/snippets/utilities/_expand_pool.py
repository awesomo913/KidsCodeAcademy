# From: scripts/dedupe_distractors.py:57
# Pad the unique distractor pool by adding stylistic variants of existing

def _expand_pool(pool: list[str], min_size: int) -> list[str]:
    """Pad the unique distractor pool by adding stylistic variants of existing
    entries until it reaches min_size. Variants must remain visibly different
    to a 7yo (different first or last word) and stay under 90 chars."""
    if len(pool) >= min_size or not pool:
        return pool
    out = list(pool)
    out_set = set(pool)
    pi = 0
    si = 0
    base_idx = 0
    # Round-robin: alternate prefix-then-suffix variant per base distractor
    while len(out) < min_size:
        base = pool[base_idx % len(pool)]
        # Lowercase first letter when prefixing so the sentence reads cleanly
        prefix_base = base[:1].lower() + base[1:] if base else base
        candidate = (VARIANT_PREFIXES[pi % len(VARIANT_PREFIXES)] + prefix_base
                     if (base_idx + pi + si) % 2 == 0
                     else base.rstrip(".!?") + VARIANT_SUFFIXES[si % len(VARIANT_SUFFIXES)])
        candidate = candidate[:90].strip()
        if candidate and candidate not in out_set:
            out.append(candidate)
            out_set.add(candidate)
        pi += 1
        si += 1
        base_idx += 1
        # Bail-out guard: if we've tried 200 combos and still can't grow, stop
        if (pi + si) > 200 and len(out) < min_size:
            break
    return out
