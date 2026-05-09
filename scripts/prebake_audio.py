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

# Voice tuning — even gentler in v0.3 (v0.2 was 148 wpm / 5500Hz)
RATE_WPM = 140
LEADING_SILENCE_MS = 250
LPF_CUTOFF_HZ = 4800.0
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


def _piper_synth_all(jobs: list[tuple[Path, str]]) -> int:
    """v0.7: bake every job via Piper TTS instead of pyttsx3 SAPI.

    Returns the number of jobs successfully synthesized.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from piper_bake import synth as _piper_synth  # type: ignore
    ok = 0
    for raw_path, text in jobs:
        try:
            if _piper_synth(text, raw_path):
                ok += 1
            else:
                log.warning("piper produced no audio for %s", raw_path.name)
        except Exception as exc:  # noqa: BLE001
            log.error("piper synth FAILED for %s: %s", raw_path.name, exc)
    return ok


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


def _collect_hint_jobs(data: dict, num: str) -> list[tuple[str, str]]:
    """Return list of (raw_filename, text) for tier 2 + tier 3 hint narrations.

    Tier 1 ("highlight") has no audio — it's a visual underline. Tier 2 and 3
    get their own short wavs so the kid can hear the hint read aloud.
    """
    jobs: list[tuple[str, str]] = []
    hints = data.get("hints") or {}
    tier2 = (hints.get("tier2") or {}).get("rephrase")
    tier3 = (hints.get("tier3") or {}).get("nudge")
    if tier2:
        jobs.append((f"lesson_{num}_hint_2.wav", str(tier2).strip()))
    if tier3:
        jobs.append((f"lesson_{num}_hint_3.wav", str(tier3).strip()))
    return jobs


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    lesson_files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not lesson_files:
        raise SystemExit(f"No lessons found at {LESSONS_DIR}")

    # v0.7: prefer Piper TTS if voice file is present. Falls back to pyttsx3
    # SAPI5 for dev boxes without piper installed.
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from piper_bake import is_available as _piper_available  # type: ignore
        use_piper = _piper_available()
    except Exception as _piper_exc:
        log.warning("piper_bake import/check failed: %s", _piper_exc)
        use_piper = False

    if use_piper:
        log.info("v0.7: using Piper TTS (en_US-amy-medium)")
        engine = None
    else:
        log.info("Piper not available; falling back to pyttsx3 SAPI5")
        engine = _load_engine()

    # Pass 1: collect (raw_path, text) pairs + (raw_path, final_path) for post-process.
    # For pyttsx3, also queue save_to_file calls; piper is invoked synchronously after.
    text_jobs: list[tuple[Path, str]] = []
    queued: list[tuple[Path, Path]] = []
    for lf in lesson_files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.error("bad JSON in %s: %s -- skipping", lf.name, exc)
            continue
        parts = lf.stem.split("_")
        num = parts[1] if len(parts) > 1 else "??"

        # Lesson narration
        lines = data.get("mascot_lines") or []
        text = " ... ".join(str(line) for line in lines).strip()
        if text:
            raw_path = RAW_DIR / f"lesson_{num}.wav"
            text_jobs.append((raw_path, text))
            queued.append((raw_path, OUT_DIR / f"lesson_{num}.wav"))
            if engine is not None:
                engine.save_to_file(text, str(raw_path))
            log.info("queued narration: %s", lf.name)
        else:
            log.warning("lesson %s has no mascot_lines, skipping narration", lf.name)

        # Hint narrations (tier 2 + tier 3)
        for raw_name, hint_text in _collect_hint_jobs(data, num):
            if not hint_text:
                continue
            raw_path = RAW_DIR / raw_name
            text_jobs.append((raw_path, hint_text))
            queued.append((raw_path, OUT_DIR / raw_name))
            if engine is not None:
                engine.save_to_file(hint_text, str(raw_path))
            log.info("queued hint: %s", raw_name)

    if use_piper:
        log.info("synthesizing %d clips via Piper...", len(text_jobs))
        ok = _piper_synth_all(text_jobs)
        log.info("piper synthesized %d/%d clips", ok, len(text_jobs))
    else:
        log.info("flushing engine for %d clips...", len(queued))
        engine.runAndWait()
        engine.stop()
    log.info("synthesis complete; post-processing...")

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
