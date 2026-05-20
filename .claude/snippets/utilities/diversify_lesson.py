# From: scripts/diversify_gates.py:166
# Rewrite Q2..Qn interactions for one lesson. Q1 untouched.

def diversify_lesson(path: Path, word_counter: list[int], dry: bool,
                     by_type: dict[str, int]) -> int:
    """Rewrite Q2..Qn interactions for one lesson. Q1 untouched.
    Updates `by_type` w/ what would be written (works in dry-run too).
    Returns count of gates rewritten."""
    data = json.loads(path.read_text(encoding="utf-8"))
    lesson_id = int(path.stem.split("_")[1])
    questions = data.get("questions") or []
    rewrites = 0
    for q_idx, q in enumerate(questions):
        if q_idx == 0:
            continue  # Q1 is the deep lesson interaction — leave it alone
        # Stride: id*7 + q_idx, mod 6 (coprime so adjacent lessons + adjacent
        # gates within a lesson differ).
        gate_idx = (lesson_id * 7 + q_idx) % len(GATE_TYPES)
        gate_type = GATE_TYPES[gate_idx]
        # v0.7.13 — history-scene timeline-order override disabled per user
        # direction (typing-only across the curriculum). Restore by un-commenting
        # if multi-type rotation returns.
        # if 5 <= lesson_id <= 16 and q_idx == 1:
        #     gate_type = "timeline-order"
        payload = _make_payload(gate_type, lesson_id, q_idx, word_counter[0])
        if gate_type == "type-this-word":
            word_counter[0] += 1
        if payload is None:
            continue
        q["interaction"] = {"type": gate_type, "payload": payload}
        rewrites += 1
        by_type[gate_type] = by_type.get(gate_type, 0) + 1
    if rewrites and not dry:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return rewrites
