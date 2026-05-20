# From: scripts/audio_qa_report.py:127
# Dedup options by audio path — same audio file may back many lessons.

def _emit_option_rows(lesson: dict, lesson_id: int, seen: set[str]) -> list[AudioRow]:
    """Dedup options by audio path — same audio file may back many lessons."""
    title = lesson.get("title", f"Lesson {lesson_id}")
    rows: list[AudioRow] = []
    for q in lesson.get("questions", []):
        qid = q.get("id", "?")
        for vi, v in enumerate(q.get("variations", [])):
            for oi, opt in enumerate(v.get("options", [])):
                audio = opt.get("_audio")
                text = opt.get("text", "")
                if not audio or not text or audio in seen:
                    continue
                if not (ROOT / audio).is_file():
                    continue
                seen.add(audio)
                rows.append(AudioRow(
                    row_id=f"L{lesson_id:02d}_q{qid}_v{vi}_o{oi}",
                    lesson_id=lesson_id,
                    lesson_title=title,
                    kind="option",
                    visible_text=text,
                    synthesis_text=_spell(text),
                    audio_path=audio,
                    qid=qid,
                    var_idx=vi,
                    has_acronym=_has_acronym(text),
                ))
    return rows
