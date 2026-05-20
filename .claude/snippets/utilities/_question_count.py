# From: scripts/expand_lessons_v3.py:2285
# 5-8 questions per lesson, deterministic from id.

def _question_count(lesson_id: int) -> int:
    """5-8 questions per lesson, deterministic from id."""
    return 5 + (lesson_id % 4)
