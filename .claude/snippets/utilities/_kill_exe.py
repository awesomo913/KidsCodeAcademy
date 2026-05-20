# From: scripts/verify_persistence.py:140
# Force-kill any running instance of the EXE.

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
