# From: scripts/gen_sfx.py:70
# 1-pole IIR low-pass: y[n] = a*x[n] + (1-a)*y[n-1].

def _lowpass(samples: Sequence[float], cutoff_hz: float = LPF_CUTOFF_HZ) -> list[float]:
    """1-pole IIR low-pass: y[n] = a*x[n] + (1-a)*y[n-1]."""
    dt = 1.0 / SR
    rc = 1.0 / (2.0 * math.pi * cutoff_hz)
    a = dt / (rc + dt)
    out: list[float] = []
    y_prev = 0.0
    for x in samples:
        y = a * x + (1.0 - a) * y_prev
        out.append(y)
        y_prev = y
    return out
