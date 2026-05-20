# From: scripts/verify_persistence.py:176
# Return (ok, reason).

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
