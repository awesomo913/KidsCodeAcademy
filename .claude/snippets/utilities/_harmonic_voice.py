# From: scripts/gen_sfx.py:52
# Fundamental + lower 2nd partial + tiny 4th partial.

def _harmonic_voice(t: float, freq_hz: float) -> float:
    """Fundamental + lower 2nd partial + tiny 4th partial.

    v0.3 tuning: 3rd harmonic dropped (was 0.18) to remove metallic edge.
    2nd reduced 0.40 -> 0.30 for a softer fundamental-led tone.
    4th at 0.05 adds gentle body without brightness.
    """
    fund = math.sin(2.0 * math.pi * freq_hz * t)
    p2 = 0.30 * math.sin(2.0 * math.pi * 2.0 * freq_hz * t)
    p4 = 0.05 * math.sin(2.0 * math.pi * 4.0 * freq_hz * t)
    return fund + p2 + p4
