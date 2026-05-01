"""Generate placeholder SFX wav files using Python's stdlib wave + struct.

Synthesizes simple short tones / chirps / arpeggios. Royalty-free by definition
(I generated them). Output: ./assets/sfx/*.wav.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "sfx"
SR = 22050
AMP = 0.45


def _envelope(i: int, total: int, attack: float = 0.02, release: float = 0.10) -> float:
    """ADSR-ish envelope: linear attack, hold, linear release."""
    t = i / max(1, total - 1)
    a = max(0.0, min(1.0, t / max(1e-6, attack)))
    r = max(0.0, min(1.0, (1.0 - t) / max(1e-6, release)))
    return min(a, r)


def _synth(freqs: list[tuple[float, float]], duration_s: float) -> list[int]:
    """Synthesize a sequence of frequency-duration pairs into 16-bit PCM samples."""
    samples: list[int] = []
    for freq, seg_s in freqs:
        n = int(SR * seg_s)
        for i in range(n):
            env = _envelope(i, n, attack=0.01, release=0.20)
            v = math.sin(2 * math.pi * freq * (i / SR))
            samples.append(int(v * env * AMP * 32767))
    # Pad / trim to duration
    target = int(SR * duration_s)
    if len(samples) < target:
        samples.extend([0] * (target - len(samples)))
    return samples[:target]


def _save(name: str, samples: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", s) for s in samples))
    print(f"wrote {path}")


def click() -> None:
    _save("click.wav", _synth([(880.0, 0.04), (1320.0, 0.04)], 0.10))


def ding() -> None:
    _save("ding.wav", _synth([(880.0, 0.10), (1320.0, 0.20)], 0.32))


def level_up() -> None:
    seq = [(523.25, 0.10), (659.25, 0.10), (783.99, 0.10), (1046.50, 0.20)]
    _save("level_up.wav", _synth(seq, 0.55))


def star_award() -> None:
    seq = [(1318.51, 0.06), (1567.98, 0.06), (1975.53, 0.18)]
    _save("star_award.wav", _synth(seq, 0.34))


def oops() -> None:
    seq = [(440.0, 0.10), (330.0, 0.18)]
    _save("oops.wav", _synth(seq, 0.32))


def page_flip() -> None:
    # Quick noise-like sweep via two close tones
    seq = [(2000.0, 0.04), (1200.0, 0.06)]
    _save("page_flip.wav", _synth(seq, 0.12))


def mascot_hi() -> None:
    seq = [(659.25, 0.10), (783.99, 0.10), (987.77, 0.18)]
    _save("mascot_hi.wav", _synth(seq, 0.42))


def type_pop() -> None:
    _save("type_pop.wav", _synth([(660.0, 0.03)], 0.05))


def main() -> None:
    click(); ding(); level_up(); star_award(); oops(); page_flip(); mascot_hi(); type_pop()


if __name__ == "__main__":
    main()
