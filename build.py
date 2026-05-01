"""Build pipeline for CC Kids Academy.

Steps:
  1. Generate icons + procedural mascot frames + sfx wavs
  2. Pre-render lesson narration to wav (TTS) -- skipped if --no-audio
  3. Run PyInstaller -> single-file CC-Kids-Academy.exe
  4. Copy exe to ../CC-Kids-Academy.exe (next to ClaudeCodeMastery.exe)
  5. Clean dist/, build/, *.spec

Run: python build.py
       python build.py --no-audio       (skip TTS, useful for fast iteration)
       python build.py --no-package     (skip pyinstaller)
"""
from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("build")

ROOT = Path(__file__).resolve().parent
PROJECT_NAME = "CC-Kids-Academy"
ENTRYPOINT = "app.py"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    log.info("$ %s", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, cwd=cwd or ROOT, check=True)


def step_assets() -> None:
    log.info("=== step 1: generating assets ===")
    run([sys.executable, "gen_icons.py"])
    run([sys.executable, "gen_mascot.py"])
    run([sys.executable, "scripts/gen_sfx.py"])


def step_audio() -> None:
    log.info("=== step 2: pre-baking lesson narration ===")
    try:
        run([sys.executable, "scripts/prebake_audio.py"])
    except subprocess.CalledProcessError as exc:
        log.warning("prebake_audio failed (%s) -- continuing without TTS", exc)


def step_package() -> None:
    log.info("=== step 3: pyinstaller ===")
    sep = ";" if sys.platform.startswith("win") else ":"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--onefile", "--windowed",
        "--name", PROJECT_NAME,
        "--add-data", f"index.html{sep}.",
        "--add-data", f"lessons{sep}lessons",
        "--add-data", f"sandbox_ai{sep}sandbox_ai",
        "--add-data", f"assets{sep}assets",
        "--add-data", f"icons{sep}icons",
        "--add-data", f"parent{sep}parent",
        "--add-data", f"vendor{sep}vendor",
    ]
    icon = ROOT / "icons" / "app.ico"
    if icon.is_file():
        cmd += ["--icon", str(icon)]
    cmd.append(ENTRYPOINT)
    run(cmd)


def step_publish() -> None:
    log.info("=== step 4: copying exe to Desktop/AI/ ===")
    src = ROOT / "dist" / f"{PROJECT_NAME}.exe"
    if not src.is_file():
        log.error("expected %s not found", src)
        return
    target = ROOT.parent / f"{PROJECT_NAME}.exe"
    shutil.copy2(src, target)
    log.info("copied -> %s", target)


def step_clean() -> None:
    log.info("=== step 5: cleaning build artifacts ===")
    for d in ("dist", "build"):
        p = ROOT / d
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
            log.info("rm %s", p)
    for f in ROOT.glob("*.spec"):
        try:
            f.unlink()
            log.info("rm %s", f)
        except OSError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-audio", action="store_true", help="skip TTS prebake")
    parser.add_argument("--no-package", action="store_true", help="skip pyinstaller + publish")
    parser.add_argument("--no-clean", action="store_true", help="leave dist/ and build/ folders")
    args = parser.parse_args()

    step_assets()
    if not args.no_audio:
        step_audio()
    if not args.no_package:
        step_package()
        step_publish()
    if not args.no_clean and not args.no_package:
        step_clean()
    log.info("BUILD DONE")


if __name__ == "__main__":
    main()
