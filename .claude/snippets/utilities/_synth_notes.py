# From: scripts/gen_sfx.py:84
# Render a sequence of notes through the warm-synth pipeline.

def _synth_notes(
    notes: Sequence[Note],
    total_duration_s: float,
    *,
    voice: Callable[[float, float], float] = _harmonic_voice,
    saturate: bool = True,
) -> list[int]:
    """Render a sequence of notes through the warm-synth pipeline."""
    raw: list[float] = []
    for note in notes:
        n = max(1, int(SR * note.duration_s))
        for i in range(n):
            t = i / SR
            env = _adsr(i, n)
            v = voice(t, note.freq_hz) * env * note.velocity
            raw.append(v)

    target_n = int(SR * total_duration_s)
    if len(raw) < target_n:
        raw.extend([0.0] * (target_n - len(raw)))
    raw = raw[:target_n]

    # Normalize to PEAK_AMP, then saturate, then low-pass.
    peak = max((abs(s) for s in raw), default=1e-6)
    scale = PEAK_AMP / max(1e-6, peak)
    scaled = [s * scale for s in raw]
    processed = [_soft_saturate(s) if saturate else s for s in scaled]
    filtered = _lowpass(processed)

    # Re-normalize after filtering (LPF can drop level slightly)
    fpeak = max((abs(s) for s in filtered), default=1e-6)
    final_scale = PEAK_AMP / max(1e-6, fpeak)
    return [int(max(-1.0, min(1.0, s * final_scale)) * 32767) for s in filtered]
