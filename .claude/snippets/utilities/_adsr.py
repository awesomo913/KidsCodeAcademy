# From: scripts/gen_sfx.py:38
# Smooth ADSR. Linear attack, exponential release. Sustain at 1.0.

def _adsr(i: int, total: int, attack_ms: float = 45.0, release_ms: float = 240.0) -> float:
    """Smooth ADSR. Linear attack, exponential release. Sustain at 1.0."""
    attack_n = max(1, int(SR * attack_ms / 1000.0))
    release_n = max(1, int(SR * release_ms / 1000.0))
    if i < attack_n:
        return i / attack_n
    rel_start = total - release_n
    if i >= rel_start:
        # Exponential decay sounds more natural than linear
        x = (i - rel_start) / max(1, total - rel_start)
        return math.exp(-3.5 * x)
    return 1.0
