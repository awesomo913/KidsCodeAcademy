# From: scripts/audio_qa_report.py:183
# Acronym-heavy rows get 2x weight, others 1x.

def weighted_sample(rows: list[AudioRow], n: int, rng: random.Random) -> list[AudioRow]:
    """Acronym-heavy rows get 2x weight, others 1x."""
    if len(rows) <= n:
        return list(rows)
    weights = [2.0 if r.has_acronym else 1.0 for r in rows]
    # weighted-without-replacement via key: -log(U) / w  (Efraimidis-Spirakis)
    keys = [(-1.0 * (rng.random() ** (1.0 / w)), idx) for idx, w in enumerate(weights)]
    keys.sort()
    chosen = [rows[idx] for _, idx in keys[:n]]
    return chosen
