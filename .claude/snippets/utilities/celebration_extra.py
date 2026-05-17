# From: scripts/gen_sfx.py:254
# Hidden voice clip used as the surprise 'MAMA MIA' celebration moment.

def celebration_extra() -> None:
    """Hidden voice clip used as the surprise 'MAMA MIA' celebration moment.

    Filename intentionally generic — does NOT mention Mario. The clip itself
    is just two cheerful notes; the action-word text supplies the wording.
    """
    seq = [
        Note(880.00, 0.15, 0.85),
        Note(1318.51, 0.30, 1.0),
    ]
    _save("celebration_extra.wav", _synth_notes(seq, 0.50))
