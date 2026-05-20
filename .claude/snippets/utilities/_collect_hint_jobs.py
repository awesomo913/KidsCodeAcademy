# From: scripts/prebake_audio.py:116
# Return list of (raw_filename, text) for tier 2 + tier 3 hint narrations.

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
