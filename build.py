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


def step_sandbox_lint() -> None:
    """v0.7: validate sandbox JSONs before bundling — abort build on any malformed file.

    Catches typos that the runtime would silently mask via the generic fallback
    string. Exit 1 from sandbox_lint.py propagates via subprocess.run(check=True).
    """
    log.info("=== step 1b: validating sandbox JSONs ===")
    run([sys.executable, "scripts/sandbox_lint.py", "--quiet"])


def step_audio() -> None:
    log.info("=== step 2: pre-baking lesson narration ===")
    try:
        run([sys.executable, "scripts/prebake_audio.py"])
    except subprocess.CalledProcessError as exc:
        log.warning("prebake_audio failed (%s) — continuing without TTS", exc)
    # v0.7.1: also bake question prompts (incremental — skips up-to-date wavs).
    log.info("=== step 2b: pre-baking question prompts ===")
    try:
        run([sys.executable, "scripts/bake_question_prompts.py"])
    except subprocess.CalledProcessError as exc:
        log.warning("bake_question_prompts failed (%s) — questions will fall back to Web Speech", exc)
    # v0.7.5: bake answer-option audio for hover-to-speak (deduped by text hash).
    log.info("=== step 2c: pre-baking answer-option audio ===")
    try:
        run([sys.executable, "scripts/bake_option_audio.py"])
    except subprocess.CalledProcessError as exc:
        log.warning("bake_option_audio failed (%s) — hover audio will fall back to Web Speech", exc)
    # v0.7.6 Phase 5: re-bake any wav whose source text contains an acronym
    # (LLM/MCQ/AI/etc) using a spelled-out variant so Piper says "L L M".
    log.info("=== step 2d: acronym preprocessing ===")
    try:
        run([sys.executable, "scripts/preprocess_acronyms.py"])
    except subprocess.CalledProcessError as exc:
        log.warning("preprocess_acronyms failed (%s) — acronyms will sound mushed", exc)
    # v0.7.6 Phase 4: compress every wav to .ogg/Opus and rewrite lesson JSON
    # _audio paths. Drops bundled audio from ~1.2 GB to ~80 MB.
    log.info("=== step 2e: compress audio to OGG/Opus ===")
    try:
        run([sys.executable, "scripts/compress_audio_ogg.py"])
    except subprocess.CalledProcessError as exc:
        log.warning("compress_audio_ogg failed (%s) — wavs will ship instead", exc)


def _build_audio_pkg() -> Path | None:
    """Phase 4: build a temp copy of `assets/` that EXCLUDES *.wav so PyInstaller
    only bundles the smaller .ogg copies. Returns the temp pkg path or None on
    failure. Caller is responsible for cleanup via shutil.rmtree.
    """
    src = ROOT / "assets"
    if not src.is_dir():
        return None
    pkg_root = ROOT / "build_pkg"
    pkg = pkg_root / "assets"
    if pkg_root.exists():
        shutil.rmtree(pkg_root, ignore_errors=True)
    def _copy_no_wav(s, names):
        # Filter exposed to copytree to skip wavs — keeps the .ogg twins.
        return [n for n in names if n.lower().endswith(".wav")]
    try:
        shutil.copytree(src, pkg, ignore=_copy_no_wav)
    except OSError as exc:
        log.warning("could not stage audio pkg: %s", exc)
        return None
    return pkg_root


def step_package() -> None:
    log.info("=== step 3: pyinstaller (target=%s) ===", "win" if _is_windows() else sys.platform)
    sep = ";" if _is_windows() else ":"
    # Stage audio assets w/o .wav to keep the exe small (Phase 4). Falls back to
    # the original assets/ folder if staging fails so a bad copytree doesn't
    # block the build. Wrapped in try/finally so the staged folder is always
    # cleaned even if PyInstaller crashes mid-build.
    pkg_root = _build_audio_pkg()
    try:
        _step_package_inner(pkg_root, sep)
    finally:
        if pkg_root and pkg_root.exists():
            shutil.rmtree(pkg_root, ignore_errors=True)


def _step_package_inner(pkg_root: Path | None, sep: str) -> None:
    assets_arg = f"{(pkg_root / 'assets')}" if pkg_root else "assets"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--onefile",
        "--name", PROJECT_NAME,
        "--add-data", f"index.html{sep}.",
        "--add-data", f"lessons{sep}lessons",
        "--add-data", f"sandbox_ai{sep}sandbox_ai",
        "--add-data", f"{assets_arg}{sep}assets",
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
        # gi (PyGObject) uses lazy/dynamic module loading that PyInstaller's
        # static analyzer cannot follow. Without --collect-all gi the resulting
        # binary errors at launch with: ModuleNotFoundError: gi.repository.
        # Same trap for pywebview's platform-specific submodules.
        cmd += [
            "--collect-all", "gi",
            "--collect-all", "webview",
            "--collect-submodules", "webview",
            "--hidden-import", "gi.repository.WebKit2",
            "--hidden-import", "gi.repository.Gtk",
            "--hidden-import", "gi.repository.GLib",
            "--hidden-import", "gi.repository.Gdk",
            "--hidden-import", "cairo",
        ]
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
    for d in ("dist", "build", "build_pkg"):
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
    step_sandbox_lint()

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
