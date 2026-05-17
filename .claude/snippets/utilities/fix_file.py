# From: scripts/fix_question_quality.py:103
# Replace problematic strings (raw text, not json-escaped — the file stores

def fix_file(path: Path) -> int:
    """Replace problematic strings (raw text, not json-escaped — the file stores
    em-dash etc. as literal Unicode chars, not \\u2014 escapes). Returns count.
    """
    text = path.read_text(encoding="utf-8")
    swaps = 0
    for bad, good in REPLACEMENTS.items():
        count = text.count(bad)
        if count:
            text = text.replace(bad, good)
            swaps += count
    if swaps:
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            print(f"FAIL {path.name}: replacement produced invalid JSON ({exc}) - skipping")
            return 0
        path.write_text(text, encoding="utf-8")
    return swaps
