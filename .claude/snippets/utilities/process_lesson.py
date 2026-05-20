# From: scripts/purge_filler_gates.py:69
# Return per-lesson stats: { q_swaps, game_swap, lesson_id }.

def process_lesson(path: Path, dry: bool) -> dict:
    """Return per-lesson stats: { q_swaps, game_swap, lesson_id }."""
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    lesson_id = int(data.get("id", 0))
    stats = {"id": lesson_id, "title": data.get("title", ""), "q_swaps": 0, "game_swap": None}

    # Question gates (Q1 + Q2+ — both swept this time)
    for q_idx, q in enumerate(data.get("questions", [])):
        gate = (q.get("interaction") or {}).get("type")
        if gate in FILLER_TYPES:
            q["interaction"] = {
                "type": "type-this-word",
                "payload": _make_typing_payload(lesson_id, q_idx),
            }
            stats["q_swaps"] += 1

    # Outer lesson `game` field — only swap if it's a filler type. Deep
    # interactions (level-painter, idea-spark, etc.) are the lesson's actual
    # mechanic and stay.
    game_type = (data.get("game") or {}).get("type")
    if game_type in FILLER_TYPES:
        data["game"] = {
            "type": "type-this-word",
            "payload": _make_typing_payload(lesson_id, 0),
        }
        stats["game_swap"] = game_type

    if (stats["q_swaps"] or stats["game_swap"]) and not dry:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return stats
