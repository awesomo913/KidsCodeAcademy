"""Persistence verification harness.

Proves that the kid's progress survives N successive EXE launch+close cycles.

What it does
------------
1. Backs up any existing %APPDATA%/KidsCodeAcademy/state.json so the kid's real
   progress is untouched.
2. Pre-seeds state.json with a fixed set of kca.* keys, including a canary
   marker key (`kca._verify_marker`) that the EXE itself never writes.
3. Loops `--cycles` times:
     a. Launch KidsCodeAcademy.exe via subprocess.Popen
     b. Sleep BOOT_WAIT_SECS for hydrate + first auto-save flush
     c. taskkill /F /IM KidsCodeAcademy.exe
     d. Read state.json + assert the marker survives AND the seeded
        kca.progress.v1 still has both completed lessons.
4. On any failure: stop loop, restore backup, exit non-zero with diagnostic.
5. On full pass: restore backup, print summary.

Run
---
    python scripts/verify_persistence.py --cycles 50
    python scripts/verify_persistence.py --cycles 5    # quick sanity check
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("verify-persistence")
ROOT = Path(__file__).resolve().parent.parent


def _appdata_root() -> Path:
    """Cross-platform per-user app data dir — mirrors app.py's _appdata_root()."""
    if os.name == "nt":  # Windows
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "KidsCodeAcademy"
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "KidsCodeAcademy"
    # Linux / Raspberry Pi
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else (Path.home() / ".local" / "share")
    return base / "KidsCodeAcademy"


def _default_exe_path() -> Path:
    """Where build.py's publish step puts the binary, per platform."""
    if os.name == "nt":
        # build.py publishes beside the repository directory. Deriving this
        # path keeps the verifier portable across usernames and Desktop/AI vs
        # Desktop/AI2 checkouts.
        return ROOT.parent / "KidsCodeAcademy.exe"
    # Linux/macOS: build.py publishes to ~/Desktop or ~/ if no Desktop
    desktop = Path.home() / "Desktop"
    target_dir = desktop if desktop.is_dir() else Path.home()
    return target_dir / "KidsCodeAcademy"


STATE_FILE = _appdata_root() / "state.json"
BACKUP_FILE = _appdata_root() / "state.json.bak.verify"
EXE_PATH = _default_exe_path()
EXE_NAME = "KidsCodeAcademy.exe" if os.name == "nt" else "KidsCodeAcademy"
MARKER_KEY = "kca._verify_marker"
MARKER_VALUE = "abc-123-FIXTURE"
BOOT_WAIT_SECS = 5.0


def _build_fixture() -> dict[str, str]:
    """Build the fixture state.json contents.

    Each value is itself a JSON-encoded string (matching how Persistence stores
    localStorage values — they are always serialized strings).
    """
    now = datetime.now(timezone.utc).isoformat()
    progress = {
        "completed": {
            "lesson_01_what_is_a_computer": now,
            "lesson_02_talking_to_claude": now,
        },
        "stickers": 2,
        "last": "lesson_02_talking_to_claude",
    }
    return {
        "kca.progress.v1": json.dumps(progress),
        "kca.sessions.v1": json.dumps([]),
        "kca.theme.v1": json.dumps("day"),
        "kca.pin.v1": json.dumps("1234"),
        "kca.transcripts.v1": json.dumps([]),
        "kca.autoplay.v1": json.dumps({"enabled": True, "delayMs": 1500}),
        MARKER_KEY: json.dumps(MARKER_VALUE),
    }


def _backup_existing() -> None:
    _appdata_root().mkdir(parents=True, exist_ok=True)
    if STATE_FILE.is_file():
        shutil.copy2(STATE_FILE, BACKUP_FILE)
        log.info("backed up existing state.json -> %s", BACKUP_FILE.name)


def _restore_backup() -> None:
    if BACKUP_FILE.is_file():
        shutil.copy2(BACKUP_FILE, STATE_FILE)
        BACKUP_FILE.unlink()
        log.info("restored kid's real state.json from backup")
    elif STATE_FILE.is_file():
        # No backup means there was no real state — leave whatever we wrote
        # OR clean it if user prefers. Default: clean it.
        STATE_FILE.unlink()
        log.info("no backup present; removed harness-seeded state.json")


def _seed_state(fixture: dict[str, str]) -> None:
    _appdata_root().mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(fixture), encoding="utf-8")


def _read_state() -> dict[str, str]:
    if not STATE_FILE.is_file():
        return {}
    raw = STATE_FILE.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    return {}


def _kill_exe() -> None:
    """Force-kill any running instance of the EXE.

    Cross-platform: Windows uses ``taskkill /F /IM`` (matches image name);
    Linux/macOS use ``pkill -f`` (matches the full command line, so the
    absolute path used by ``_launch_exe`` still hits).
    """
    if os.name == "nt":
        # /F = force, /IM = image name. Multiple instances killed in one call.
        subprocess.run(
            ["taskkill", "/F", "/IM", EXE_NAME],
            check=False,
            capture_output=True,
        )
    else:
        # -f matches against full command line — covers absolute-path launches.
        # Exit code 1 just means "no matching process" — harmless here.
        subprocess.run(
            ["pkill", "-f", EXE_NAME],
            check=False,
            capture_output=True,
        )
    # Give the OS a moment to release file handles
    time.sleep(0.5)


def _launch_exe() -> subprocess.Popen[bytes]:
    if not EXE_PATH.is_file():
        raise SystemExit(f"EXE not found at {EXE_PATH} — run python build.py first")
    return subprocess.Popen(
        [str(EXE_PATH)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _check_state(state: dict[str, str], cycle: int) -> tuple[bool, str]:
    """Return (ok, reason)."""
    # Marker must survive
    marker = state.get(MARKER_KEY)
    if marker is None:
        return False, f"cycle {cycle}: marker key {MARKER_KEY!r} missing from state.json"
    try:
        if json.loads(marker) != MARKER_VALUE:
            return False, f"cycle {cycle}: marker value mismatch (got {marker!r})"
    except json.JSONDecodeError:
        return False, f"cycle {cycle}: marker value is not valid JSON ({marker!r})"

    # Progress must still have both seeded completions
    prog_raw = state.get("kca.progress.v1")
    if not prog_raw:
        return False, f"cycle {cycle}: kca.progress.v1 missing from state.json"
    try:
        prog = json.loads(prog_raw)
    except json.JSONDecodeError:
        return False, f"cycle {cycle}: kca.progress.v1 is not valid JSON"
    completed = (prog or {}).get("completed", {})
    expected = {"lesson_01_what_is_a_computer", "lesson_02_talking_to_claude"}
    missing = expected - set(completed.keys())
    if missing:
        return False, f"cycle {cycle}: missing completed lessons: {sorted(missing)}"
    if (prog or {}).get("stickers") != 2:
        return False, f"cycle {cycle}: stickers expected 2, got {prog.get('stickers')!r}"
    return True, ""


def main() -> int:
    global EXE_PATH, EXE_NAME
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=50)
    parser.add_argument("--boot-wait", type=float, default=BOOT_WAIT_SECS,
                        help="Seconds to let the EXE boot + flush state on each cycle")
    parser.add_argument("--exe", type=Path, default=EXE_PATH,
                        help=f"EXE to verify (default: {EXE_PATH})")
    args = parser.parse_args()

    EXE_PATH = args.exe.expanduser().resolve()
    EXE_NAME = EXE_PATH.name

    if not EXE_PATH.is_file():
        log.error("EXE not found at %s", EXE_PATH)
        log.error("Run `python build.py` from the project root first.")
        return 2

    log.info("=== Persistence verification: %d cycles, %.1fs boot wait ===",
             args.cycles, args.boot_wait)

    _backup_existing()
    fixture = _build_fixture()
    _seed_state(fixture)
    log.info("seeded state.json with %d keys (marker = %s)", len(fixture), MARKER_VALUE)

    started = time.monotonic()
    failed_cycle = 0
    failure_reason = ""

    try:
        for i in range(1, args.cycles + 1):
            cycle_start = time.monotonic()
            proc = _launch_exe()
            time.sleep(args.boot_wait)
            _kill_exe()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()

            state = _read_state()
            ok, reason = _check_state(state, i)
            cycle_secs = time.monotonic() - cycle_start
            if not ok:
                log.error("FAIL %d/%d in %.1fs: %s", i, args.cycles, cycle_secs, reason)
                failed_cycle = i
                failure_reason = reason
                break
            log.info("PASS %d/%d in %.1fs", i, args.cycles, cycle_secs)
    finally:
        _restore_backup()

    elapsed = time.monotonic() - started
    if failed_cycle:
        log.error("=" * 60)
        log.error("FAILED at cycle %d/%d after %.1fs", failed_cycle, args.cycles, elapsed)
        log.error("Reason: %s", failure_reason)
        return 1

    mean = elapsed / args.cycles if args.cycles else 0.0
    log.info("=" * 60)
    log.info("PASSED %d/%d cycles in %.1fs (mean %.1fs/cycle)",
             args.cycles, args.cycles, elapsed, mean)
    return 0


if __name__ == "__main__":
    sys.exit(main())
