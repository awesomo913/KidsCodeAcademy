"""Pre-render lesson narration to wav files using pyttsx3 (Windows SAPI).

Two-pass design (avoids SAPI hang from per-lesson runAndWait):
  Pass 1: queue ALL `engine.save_to_file()` calls, then ONE `engine.runAndWait()`.
          Output: raw wavs in `assets/audio_raw/lesson_NN.wav`.
  Pass 2: post-process each raw wav with stdlib `wave`:
            - prepend 250 ms of silence (gentler "warm-up")
            - 1-pole low-pass at ~5500 Hz to soften SAPI's edges
            - slight gain compensation
          Output: `assets/audio/lesson_NN.wav`. Raw dir is removed at the end.

Shipped exe has zero TTS dependency at runtime.

Run: `python scripts/prebake_audio.py`
"""
from __future__ import annotations

import json
import logging
import math
import shutil
import struct
import wave
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("prebake-audio")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
OUT_DIR = ROOT / "assets" / "audio"
RAW_DIR = ROOT / "assets" / "audio_raw"

# Voice tuning — slower + gentler than v0.1 (was 165 wpm)
RATE_WPM = 148
LEADING_SILENCE_MS = 250
LPF_CUTOFF_HZ = 5500.0
POST_GAIN = 1.10


def _load_engine():
    try:
        import pyttsx3
    except ImportError as exc:
        raise SystemExit("pyttsx3 not installed. Run: uv pip install -r requirements.txt") from exc

    engine = pyttsx3.init()
    engine.setProperty("rate", RATE_WPM)
    voices = engine.getProperty("voices") or []
    for v in voices:
        name = (getattr(v, "name", "") or "").lower()
        if "zira" in name or "female" in name:
            engine.setProperty("voice", v.id)
            break
    return engine


def _post_process(in_path: Path, out_path: Path) -> None:
    """Read SAPI wav, add leading silence + low-pass + slight gain, write final wav."""
    with wave.open(str(in_path), "rb") as r:
        n_channels = r.getnchannels()
        sample_width = r.getsampwidth()
        sr = r.getframerate()
        n_frames = r.getnframes()
        raw = r.readframes(n_frames)

    if sample_width != 2:
        log.warning("unexpected sample_width=%d for %s; copying through", sample_width, in_path)
        out_path.write_bytes(in_path.read_bytes())
        return

    fmt = f"<{n_frames * n_channels}h"
    samples = list(struct.unpack(fmt, raw))
    if n_channels > 1:
        per_chan: list[list[int]] = [samples[c::n_channels] for c in range(n_channels)]
        samples = [sum(c) // n_channels for c in zip(*per_chan)]
    floats = [s / 32768.0 for s in samples]

    dt = 1.0 / sr
    rc = 1.0 / (2.0 * math.pi * LPF_CUTOFF_HZ)
    a = dt / (rc + dt)
    filtered: list[float] = []
    y_prev = 0.0
    for x in floats:
        y = a * x + (1.0 - a) * y_prev
        filtered.append(y)
        y_prev = y

    final = [max(-1.0, min(1.0, s * POST_GAIN)) for s in filtered]

    silence = [0.0] * int(sr * LEADING_SILENCE_MS / 1000.0)
    final_with_silence = silence + final

    out_int16 = struct.pack(
        f"<{len(final_with_silence)}h",
        *(int(s * 32767) for s in final_with_silence),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(out_int16)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    lesson_files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not lesson_files:
        raise SystemExit(f"No lessons found at {LESSONS_DIR}")

    engine = _load_engine()

    # Pass 1: queue every save_to_file, then one runAndWait
    queued: list[tuple[Path, Path]] = []
    for lf in lesson_files:
        data = json.loads(lf.read_text(encoding="utf-8"))
        lines = data.get("mascot_lines") or []
        text = " ... ".join(str(line) for line in lines).strip()
        if not text:
            log.warning("lesson %s has no mascot_lines, skipping", lf.name)
            continue
        num = lf.stem.split("_")[1]
        raw_path = RAW_DIR / f"lesson_{num}.wav"
        engine.save_to_file(text, str(raw_path))
        final_path = OUT_DIR / f"lesson_{num}.wav"
        queued.append((raw_path, final_path))
        log.info("queued %s", lf.name)

    log.info("flushing engine for %d lessons...", len(queued))
    engine.runAndWait()
    engine.stop()
    log.info("flush complete; post-processing...")

    # Pass 2: post-process every raw wav
    for raw_path, final_path in queued:
        if not raw_path.is_file() or raw_path.stat().st_size == 0:
            log.error("missing/empty raw wav: %s", raw_path)
            continue
        _post_process(raw_path, final_path)
        log.info("baked %s (%.1f KB)", final_path.name, final_path.stat().st_size / 1024)

    # Clean up raw dir so it doesn't ship with the exe
    try:
        shutil.rmtree(RAW_DIR, ignore_errors=True)
    except OSError as exc:
        log.warning("could not remove %s: %s", RAW_DIR, exc)

    log.info("done. wavs at %s", OUT_DIR)


if __name__ == "__main__":
    main()
