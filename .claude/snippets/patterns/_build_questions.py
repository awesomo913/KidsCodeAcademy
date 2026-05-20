# From: scripts/expand_lessons_v2.py:1221

def _build_questions(lesson: dict[str, Any], seed: dict[str, Any]) -> list[dict[str, Any]]:
    n = _question_count(lesson["id"])
    questions: list[dict[str, Any]] = []

    # Q0 — keeps the original lesson.game as its gate; MCQ uses the lesson topic
    q0_interaction = lesson.get("game") or GATE_TEMPLATES[0]
    questions.append({
        "id": "q1",
        "interaction": q0_interaction,
        "variations": [
            _build_variation(FRAMES[v % len(FRAMES)], PARAPHRASES[v % len(PARAPHRASES)], seed, v, 0)
            for v in range(5)
        ],
    })

    # Q1..QN-1 — small rotating gates, MCQ frames cycle through the 5 frames
    for i in range(1, n):
        gate = GATE_TEMPLATES[i % len(GATE_TEMPLATES)]
        frame = FRAMES[i % len(FRAMES)]
        questions.append({
            "id": f"q{i + 1}",
            "interaction": gate,
            "variations": [
                _build_variation(frame, PARAPHRASES[v], seed, v, i)
                for v in range(5)
            ],
        })

    return questions
