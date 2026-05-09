"""Compress every WAV in assets/audio/ to OGG/Opus, then rewrite lesson JSON
`_audio` paths to point at the new .ogg files.

WebView2 (Windows) and WebKitGTK (Pi) both decode <audio src="*.ogg"> natively
via libopus / Media Foundation. Opus at 24kbps mono is transparent for speech
and lands ~10-15× smaller than 22kHz WAV.

Run:
    python scripts/compress_audio_ogg.py            # incremental
    python scripts/compress_audio_ogg.py --force    # re-compress everything
    python scripts/compress_audio_ogg.py --dry-run  # report only

Notes:
  * Originals in assets/audio/{q,o,lessons,hints} are left in place so future
    re-bakes can re-encode without re-running Piper.
  * .gitignore should add `assets/audio/**/*.wav` after this lands so only the
    OGGs ship; the WAVs stay local.
  * ffmpeg location is auto-detected from PATH or the workspace's bundled copy
    at ~/Desktop/AI/ffmpeg/ffmpeg-8.1-essentials_build/bin/ffmpeg.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ogg")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
AUDIO_DIR   = ROOT / "assets" / "audio"

OPUS_BITRATE = "24k"   # transparent for mono speech


def _find_ffmpeg() -> str:
    # Prefer system PATH, then fall back to the workspace bundled copy.
    p = shutil.which("ffmpeg")
    if p:
        return p
    bundled = Path.home() / "Desktop" / "AI" / "ffmpeg" / "ffmpeg-8.1-essentials_build" / "bin" / "ffmpeg.exe"
    if bundled.is_file():
        return str(bundled)
    bundled2 = Path.home() / "Desktop" / "AI" / "ffmpeg" / "ffmpeg-8.1-essentials_build" / "bin" / "ffmpeg"
    if bundled2.is_file():
        return str(bundled2)
    raise RuntimeError("ffmpeg not found in PATH or bundled location")


def convert_wav_to_ogg(ffmpeg: str, src: Path, dst: Path) -> bool:
    """Encode `src` (wav) → `dst` (ogg/opus). Returns True on success."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-loglevel", "error",
        "-i", str(src),
        "-ac", "1",            # force mono
        "-c:a", "libopus",
        "-b:a", OPUS_BITRATE,
        "-application", "voip",  # speech optimization
        str(dst),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        log.error("ffmpeg FAIL %s: %s", src.name, exc.stderr.strip())
        return False
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    try:
        ffmpeg = _find_ffmpeg()
    except RuntimeError as exc:
        log.error("%s", exc)
        return 1
    log.info("using ffmpeg: %s", ffmpeg)

    wavs = sorted(AUDIO_DIR.rglob("*.wav"))
    log.info("found %d wav files under %s", len(wavs), AUDIO_DIR)
    if not wavs:
        return 0

    converted = 0
    skipped = 0
    errors = 0
    bytes_before = 0
    bytes_after = 0
    for wav in wavs:
        ogg = wav.with_suffix(".ogg")
        bytes_before += wav.stat().st_size
        if not args.force and ogg.is_file() and ogg.stat().st_mtime >= wav.stat().st_mtime:
            skipped += 1
            bytes_after += ogg.stat().st_size
            continue
        if args.dry_run:
            converted += 1
            continue
        ok = convert_wav_to_ogg(ffmpeg, wav, ogg)
        if ok:
            converted += 1
            bytes_after += ogg.stat().st_size
        else:
            errors += 1
            if ogg.is_file():
                bytes_after += ogg.stat().st_size

    if args.dry_run:
        log.info("DRY-RUN: would convert %d (skipped %d already current)", converted, skipped)
        return 0

    log.info("conversion: converted=%d skipped=%d errors=%d", converted, skipped, errors)
    log.info("size: wavs %.1f MB -> oggs %.1f MB (%.1fx smaller)",
             bytes_before / 1e6, bytes_after / 1e6,
             bytes_before / max(1, bytes_after))

    # Rewrite _audio paths in lesson JSON: .wav -> .ogg
    log.info("rewriting _audio paths in lesson JSON...")
    rewritten_files = 0
    rewritten_paths = 0
    for lf in sorted(LESSONS_DIR.glob("lesson_*.json")):
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        changed = False
        for q in data.get("questions") or []:
            for v in q.get("variations") or []:
                a = v.get("_audio")
                if isinstance(a, str) and a.endswith(".wav"):
                    v["_audio"] = a[:-4] + ".ogg"
                    changed = True
                    rewritten_paths += 1
                for opt in v.get("options") or []:
                    a = opt.get("_audio")
                    if isinstance(a, str) and a.endswith(".wav"):
                        opt["_audio"] = a[:-4] + ".ogg"
                        changed = True
                        rewritten_paths += 1
        if changed:
            lf.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            rewritten_files += 1

    log.info("rewrote %d paths in %d lesson files", rewritten_paths, rewritten_files)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
