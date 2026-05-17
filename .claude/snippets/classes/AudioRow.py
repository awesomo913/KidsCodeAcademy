# From: scripts/audio_qa_report.py:64

@dataclass(frozen=True)
class AudioRow:
    """A single auditable audio entry."""
    row_id: str
    lesson_id: int
    lesson_title: str
    kind: str            # narration | prompt | option
    visible_text: str    # what the kid SEES (or hears as they read along)
    synthesis_text: str  # what was sent to Piper (acronyms spelled out)
    audio_path: str      # relative path under project root
    qid: str = ""
    var_idx: int = -1
    has_acronym: bool = False
