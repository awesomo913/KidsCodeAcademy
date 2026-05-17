# From: scripts/swap_click_to_type.py:86
# Walk a lesson's questions[] and:

def swap_lesson(path: Path, counter: list[int]) -> int:
    """Walk a lesson's questions[] and:
      (a) convert any leftover `click-the-thing` gate → `type-this-word`, AND
      (b) refresh every existing `type-this-word` payload w/ a new word from
          the lesson's pool (clean pool for L01-04, full pool elsewhere).
    Both produce a deterministic walk: re-runs are idempotent (same input → same output).
    Returns count of payloads written.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    lesson_id = int(path.stem.split("_")[1])
    pool = _pool_for(lesson_id)
    questions = data.get("questions") or []
    swaps = 0
    for q in questions:
        interaction = q.get("interaction") or {}
        kind = interaction.get("type")
        if kind not in ("click-the-thing", "type-this-word"):
            continue
        word = pool[counter[0] % len(pool)]
        counter[0] += 1
        q["interaction"] = {
            "type": "type-this-word",
            "payload": make_type_payload(word),
        }
        swaps += 1
    if swaps:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return swaps
