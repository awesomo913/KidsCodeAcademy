# From: scripts/expand_lessons_v2.py:1256
# Load lesson_NN.json, attach questions[], write back. Returns True on OK.

def expand_lesson(path: Path) -> bool:
    """Load lesson_NN.json, attach questions[], write back. Returns True on OK."""
    raw = path.read_text(encoding="utf-8")
    lesson: dict[str, Any] = json.loads(raw)
    lesson_id = int(lesson.get("id") or 0)
    seed = SEEDS.get(lesson_id)
    if seed is None:
        log.warning("no seed for lesson %d (%s); leaving alone", lesson_id, path.name)
        return False

    lesson["questions"] = _build_questions(lesson, seed)
    lesson["schema"] = "v2"  # marker so engine knows to use questions[]

    path.write_text(json.dumps(lesson, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("expanded %s — %d questions × %d variations",
             path.name, len(lesson["questions"]), len(lesson["questions"][0]["variations"]))
    return True
