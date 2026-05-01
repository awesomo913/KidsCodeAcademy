"""Pre-render lesson narration to wav files using pyttsx3 (Windows SAPI).

Reads each lessons/*.json, joins mascot_lines, dumps to assets/audio/lesson_NN.wav.
Run once during build.py. Shipped exe has zero TTS dependency at runtime.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("prebake-audio")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
OUT_DIR = ROOT / "assets" / "audio"
RATE_WPM = 165


def _load_engine():
    try:
        import pyttsx3
    except ImportError as exc:
        raise SystemExit("pyttsx3 not installed. Run: uv pip install -r requirements.txt") from exc

    engine = pyttsx3.init()
    engine.setProperty("rate", RATE_WPM)
    # Prefer Zira (kid-friendly female voice) on Windows; fall back gracefully.
    voices = engine.getProperty("voices") or []
    for v in voices:
        name = (getattr(v, "name", "") or "").lower()
        if "zira" in name or "female" in name:
            engine.setProperty("voice", v.id)
            break
    return engine


def _bake_one(engine, lesson_path: Path, out_path: Path) -> None:
    data = json.loads(lesson_path.read_text(encoding="utf-8"))
    lines = data.get("mascot_lines") or []
    text = " ... ".join(str(line) for line in lines).strip()
    if not text:
        log.warning("lesson %s has no mascot_lines, skipping", lesson_path.name)
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    engine.save_to_file(text, str(out_path))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lesson_files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not lesson_files:
        raise SystemExit(f"No lessons found at {LESSONS_DIR}")

    engine = _load_engine()
    queued = 0
    for lf in lesson_files:
        # Map lesson_07_if_then_choices.json -> lesson_07.wav
        num = lf.stem.split("_")[1]
        out = OUT_DIR / f"lesson_{num}.wav"
        _bake_one(engine, lf, out)
        queued += 1
        log.info("queued %s -> %s", lf.name, out.name)

    log.info("running engine for %d lessons...", queued)
    engine.runAndWait()
    engine.stop()
    log.info("done. wavs at %s", OUT_DIR)


if __name__ == "__main__":
    main()
