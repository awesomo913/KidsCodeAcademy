"""Generate warm, kid-friendly SFX wav files using only stdlib.

Synthesis pipeline per voice:
  1. Sum harmonics: fundamental + 2x partial (0.4 amp) + 3x partial (0.18 amp)
  2. Apply ADSR envelope: 28 ms attack, exponential release
  3. Soft saturation via tanh (gentle warmth, no hard clipping)
  4. 1-pole low-pass IIR filter (~5 kHz cutoff) — kills harshness
  5. Mix at 16-bit PCM, 22050 Hz mono

Output: ./assets/sfx/*.wav (CC0, generated locally).
"""
from __future__ import annotations

import logging
import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("gen_sfx")

OUT = Path(__file__).resolve().parent.parent / "assets" / "sfx"
SR: int = 22050
PEAK_AMP: float = 0.42  # leave headroom before saturation
LPF_CUTOFF_HZ: float = 5200.0  # roll off harshness above this


@dataclass(frozen=True)
class Note:
    freq_hz: float
    duration_s: float
    velocity: float = 1.0  # per-note amplitude scalar (0..1)


def _adsr(i: int, total: int, attack_ms: float = 28.0, release_ms: float = 220.0) -> float:
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


def _harmonic_voice(t: float, freq_hz: float) -> float:
    """Fundamental + 2 partials. Warmer than a pure sine."""
    fund = math.sin(2.0 * math.pi * freq_hz * t)
    p2 = 0.40 * math.sin(2.0 * math.pi * 2.0 * freq_hz * t)
    p3 = 0.18 * math.sin(2.0 * math.pi * 3.0 * freq_hz * t)
    return fund + p2 + p3


def _soft_saturate(x: float, drive: float = 1.15) -> float:
    """tanh-based soft clip. drive < 1.0 = transparent, > 1.0 = warmer."""
    return math.tanh(x * drive) / math.tanh(drive)


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


def _save(name: str, samples: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", s) for s in samples))
    log.info("wrote %s", path)


# === Per-SFX recipes ============================================
# Notes use C major / pentatonic intervals — kid-friendly.

def click() -> None:
    _save("click.wav", _synth_notes(
        [Note(659.25, 0.05, 0.7), Note(987.77, 0.06, 0.6)],
        0.14,
    ))


def ding() -> None:
    _save("ding.wav", _synth_notes(
        [Note(783.99, 0.09, 0.85), Note(1174.66, 0.22, 1.0)],
        0.36,
    ))


def level_up() -> None:
    # Warm major arpeggio — C E G C
    seq = [
        Note(523.25, 0.11, 0.85),
        Note(659.25, 0.11, 0.90),
        Note(783.99, 0.11, 0.95),
        Note(1046.50, 0.30, 1.0),
    ]
    _save("level_up.wav", _synth_notes(seq, 0.70))


def star_award() -> None:
    # Sparkle: short rising thirds in upper octave
    seq = [
        Note(1318.51, 0.06, 0.70),
        Note(1567.98, 0.06, 0.85),
        Note(1975.53, 0.22, 1.0),
    ]
    _save("star_award.wav", _synth_notes(seq, 0.40))


def oops() -> None:
    # Gentle descending second — friendly, not scary
    seq = [Note(523.25, 0.10, 0.75), Note(440.00, 0.20, 0.75)]
    _save("oops.wav", _synth_notes(seq, 0.34))


def page_flip() -> None:
    # Quick airy chirp
    seq = [Note(1244.51, 0.04, 0.55), Note(932.33, 0.05, 0.45)]
    _save("page_flip.wav", _synth_notes(seq, 0.12))


def mascot_hi() -> None:
    # Cheery upward 4-3-1 motif
    seq = [
        Note(659.25, 0.09, 0.80),
        Note(783.99, 0.09, 0.85),
        Note(1046.50, 0.18, 1.0),
    ]
    _save("mascot_hi.wav", _synth_notes(seq, 0.40))


def type_pop() -> None:
    # Single soft pop — quieter than v1
    _save("type_pop.wav", _synth_notes([Note(659.25, 0.025, 0.6)], 0.05))


# === Celebration / firework SFX (NEW for v0.2) ===================

def firework_pop() -> None:
    # Whistle + bang: rising pitch then a low boom
    notes = [
        Note(880.0, 0.18, 0.55),   # rising whistle
        Note(1318.51, 0.10, 0.80), # peak
        Note(220.0, 0.22, 0.95),   # boom (low octave)
    ]
    _save("firework_pop.wav", _synth_notes(notes, 0.55))


def firework_burst() -> None:
    # Triad burst — C major chord all at once
    samples_a = _synth_notes([Note(523.25, 0.30, 0.75)], 0.40, saturate=False)
    samples_b = _synth_notes([Note(659.25, 0.30, 0.75)], 0.40, saturate=False)
    samples_c = _synth_notes([Note(783.99, 0.30, 0.85)], 0.40, saturate=False)
    mixed = [
        max(-32767, min(32767, a + b + c)) // 3
        for a, b, c in zip(samples_a, samples_b, samples_c)
    ]
    _save("firework_burst.wav", mixed)


def huge_yay() -> None:
    # Big fanfare: ascending C major scale + triumphant high note
    seq = [
        Note(523.25, 0.10, 0.75),
        Note(659.25, 0.10, 0.80),
        Note(783.99, 0.10, 0.85),
        Note(880.00, 0.10, 0.90),
        Note(1046.50, 0.10, 0.95),
        Note(1318.51, 0.32, 1.0),
    ]
    _save("huge_yay.wav", _synth_notes(seq, 0.95))


def tada() -> None:
    # Classic "ta-da!" — short staccato + held cheerful note
    seq = [
        Note(659.25, 0.08, 0.85),
        Note(783.99, 0.06, 0.0),  # tiny gap
        Note(1046.50, 0.30, 1.0),
    ]
    _save("tada.wav", _synth_notes(seq, 0.50))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # v0.1 sounds — re-rendered with warmer pipeline
    click()
    ding()
    level_up()
    star_award()
    oops()
    page_flip()
    mascot_hi()
    type_pop()
    # v0.2 firework / celebration sounds
    firework_pop()
    firework_burst()
    huge_yay()
    tada()


if __name__ == "__main__":
    main()
