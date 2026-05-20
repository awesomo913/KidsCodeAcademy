# From: scripts/prebake_audio.py:47
# v0.7: bake every job via Piper TTS instead of pyttsx3 SAPI.

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
