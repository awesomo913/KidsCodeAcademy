# From: scripts/verify_persistence.py:77
# Build the fixture state.json contents.

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
