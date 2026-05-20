# From: scripts/bake_question_prompts.py:34
# Stable relative path used by both bake + runtime.

def _audio_relpath(num: str, qid: str, vidx: int) -> str:
    """Stable relative path used by both bake + runtime."""
    return f"assets/audio/q/lesson_{num}_{qid}_v{vidx}.wav"
