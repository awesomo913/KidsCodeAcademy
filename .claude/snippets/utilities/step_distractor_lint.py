# From: build.py:67
# Block ship if any wrong-answer text repeats > 3 times in one question.

def step_distractor_lint() -> None:
    """Block ship if any wrong-answer text repeats > 3 times in one question.
    Defeats the kid's pattern-matching memorization. dedupe_distractors.py
    auto-fixes locally; this lint enforces the cap at build time."""
    log.info("=== step 1c: distractor dedupe check ===")
    run([sys.executable, "scripts/check_distractor_dupes.py", "--quiet"])
