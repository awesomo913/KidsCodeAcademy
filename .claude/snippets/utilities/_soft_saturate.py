# From: scripts/gen_sfx.py:65
# tanh-based soft clip. drive < 1.0 = transparent, > 1.0 = warmer.

def _soft_saturate(x: float, drive: float = 1.05) -> float:
    """tanh-based soft clip. drive < 1.0 = transparent, > 1.0 = warmer."""
    return math.tanh(x * drive) / math.tanh(drive)
