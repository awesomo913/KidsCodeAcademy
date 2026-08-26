"""Generate the bundled, copyright-free ambient music loop.

The loop is intentionally calm, lyric-free, and quieter than narration.  It
uses only deterministic synthesized tones, so builds never depend on a stock
music download or an unclear license.
"""
from __future__ import annotations

import math
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "bg_music" / "loop.ogg"
RATE = 48_000
DURATION = 24.0


def _tone(freq: float, t: float) -> float:
    return math.sin(2 * math.pi * freq * t) + 0.16 * math.sin(4 * math.pi * freq * t)


def _make_samples() -> list[tuple[float, float]]:
    # Six four-second chords. Each chord fades fully at its boundaries, making
    # the final OGG safe to loop without a click.
    chords = [
        (130.81, 164.81, 196.00, 246.94),  # Cmaj7
        (110.00, 130.81, 164.81, 196.00),  # Am7
        (87.31, 130.81, 164.81, 196.00),   # Fmaj7
        (98.00, 146.83, 196.00, 220.00),   # Gsus2
        (110.00, 146.83, 174.61, 220.00),  # Dm6/A
        (98.00, 130.81, 164.81, 196.00),   # gentle G/C return
    ]
    arpeggio = (523.25, 659.25, 783.99, 987.77, 783.99, 659.25)
    out: list[tuple[float, float]] = []
    for n in range(int(RATE * DURATION)):
        t = n / RATE
        chord_index = min(len(chords) - 1, int(t // 4.0))
        local = t % 4.0
        pad_env = math.sin(math.pi * local / 4.0) ** 1.4
        pad = sum(_tone(freq, t) for freq in chords[chord_index]) / len(chords[chord_index])

        beat = int(t * 2) % len(arpeggio)
        beat_t = (t * 2) % 1.0
        bell_env = math.exp(-6.5 * beat_t) * (math.sin(math.pi * local / 4.0) ** 0.7)
        bell = math.sin(2 * math.pi * arpeggio[beat] * t) * bell_env

        # Slowly moving stereo field, kept subtle so headphones remain comfy.
        pan = 0.5 + 0.22 * math.sin(2 * math.pi * t / DURATION)
        center = 0.20 * pad * pad_env
        sparkle = 0.055 * bell
        out.append((center + sparkle * (1.0 - pan), center + sparkle * pan))
    return out


def main() -> int:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ffmpeg is required to generate background music")
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    samples = _make_samples()
    peak = max(max(abs(left), abs(right)) for left, right in samples) or 1.0
    gain = 0.52 / peak
    with tempfile.TemporaryDirectory(prefix="kca_music_") as temp_dir:
        wav_path = Path(temp_dir) / "loop.wav"
        with wave.open(str(wav_path), "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            frames = bytearray()
            for left, right in samples:
                frames.extend(struct.pack("<hh", int(left * gain * 32767), int(right * gain * 32767)))
            wav.writeframes(frames)
        subprocess.run([
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav_path),
            "-c:a", "libopus", "-b:a", "96k", "-vbr", "on", "-application", "audio",
            str(OUTPUT),
        ], check=True)
    print(f"generated {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
