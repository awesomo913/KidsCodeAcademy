# From: scripts/gen_sfx.py:31

@dataclass(frozen=True)
class Note:
    freq_hz: float
    duration_s: float
    velocity: float = 1.0  # per-note amplitude scalar (0..1)
