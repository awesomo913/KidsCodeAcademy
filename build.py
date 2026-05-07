"""Build pipeline for Kids Code Academy.

Cross-platform: Windows -> KidsCodeAcademy.exe; Linux/Pi -> KidsCodeAcademy (binary).

Steps:
  1. Generate icons + procedural mascot frames + sfx wavs
  2. Pre-render lesson narration to wav (TTS) — skipped if --no-audio.
     Auto-skipped on Linux/Pi (audio is already pre-baked + committed; pyttsx3 +
     SAPI Zira is Windows-only and we don't want espeak's robotic voice).
  3. Run PyInstaller -> single binary
  4. Copy binary to ../KidsCodeAcademy(.exe)
  5. Clean dist/, build/, *.spec

Run:
       python build.py                  # full build (default for the host platform)
       python build.py --no-audio       # skip TTS, useful for fast iteration
       python build.py --no-package     # skip pyinstaller
       python build.py --target=pi      # explicit Pi build (otherwise auto-detected)
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
PROJECT_NAME = "KidsCodeAcademy"
ENTRYPOINT = "app.py"


def _is_windows() -> bool:
    return sys.platform.startswith("win")


def _binary_name() -> str:
    return f"{PROJECT_NAME}.exe" if _is_windows() else PROJECT_NAME


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
        log.warning("prebake_audio failed (%s) — continuing without TTS", exc)


def step_package() -> None:
    log.info("=== step 3: pyinstaller (target=%s) ===", "win" if _is_windows() else sys.platform)
    sep = ";" if _is_windows() else ":"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--onefile",
        "--name", PROJECT_NAME,
        "--add-data", f"index.html{sep}.",
        "--add-data", f"lessons{sep}lessons",
        "--add-data", f"sandbox_ai{sep}sandbox_ai",
        "--add-data", f"assets{sep}assets",
        "--add-data", f"icons{sep}icons",
        "--add-data", f"parent{sep}parent",
        "--add-data", f"vendor{sep}vendor",
    ]

    if _is_windows():
        # --windowed suppresses the Windows console. On Linux/Pi we keep stdout
        # visible so kid/parent can see startup logs in case GTK fails to load.
        cmd.append("--windowed")
        icon = ROOT / "icons" / "app.ico"
        if icon.is_file():
            cmd += ["--icon", str(icon)]
    else:
        # Linux: use PNG for the icon (PyInstaller accepts .png on Linux).
        icon = ROOT / "icons" / "icon-512.png"
        if icon.is_file():
            cmd += ["--icon", str(icon)]
        # WebKitGTK runtime libs ship via OS packages; we don't bundle them.

    cmd.append(ENTRYPOINT)
    run(cmd)


def step_publish() -> None:
    binary = _binary_name()
    log.info("=== step 4: copying %s to Desktop ===", binary)
    src = ROOT / "dist" / binary
    if not src.is_file():
        log.error("expected %s not found", src)
        return

    if _is_windows():
        # Lands next to ClaudeCodeMastery.exe on the dev machine
        target = ROOT.parent / binary
    else:
        # Pi/Linux: drop on the user's Desktop if it exists, else home dir.
        desktop = Path.home() / "Desktop"
        target_dir = desktop if desktop.is_dir() else Path.home()
        target = target_dir / binary

    shutil.copy2(src, target)
    if not _is_windows():
        # Make it executable for double-click on Pi/Linux file managers
        target.chmod(0o755)
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
    parser.add_argument("--target", choices=["auto", "win", "pi", "linux", "mac"], default="auto",
                        help="explicit target (default: auto-detect from host)")
    args = parser.parse_args()

    if args.target != "auto":
        log.info("explicit target=%s requested (host=%s)", args.target, sys.platform)

    step_assets()

    # Audio: skip on non-Windows by default (pyttsx3 + SAPI Zira is Windows-only;
    # the wavs in assets/audio/ are already pre-baked and committed to the repo).
    if not args.no_audio:
        if _is_windows():
            step_audio()
        else:
            log.info("=== step 2: skipping TTS prebake (non-Windows host) ===")

    if not args.no_package:
        step_package()
        step_publish()
    if not args.no_clean and not args.no_package:
        step_clean()
    log.info("BUILD DONE")


if __name__ == "__main__":
    main()
