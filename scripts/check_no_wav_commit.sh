#!/bin/bash
# Pre-commit guard — abort if any *.wav under assets/audio/ is being staged.
#
# Why: wav originals live in assets/audio/ during local builds (Piper bakes wavs,
# compress_audio_ogg.py converts them to .ogg siblings). The .gitignore covers
# them, but already-tracked wavs slip through. This script makes a future
# accidental re-track noisy + blocking instead of silently bloating the repo.
#
# Hook into .git/hooks/pre-commit by running:
#   bash scripts/install_hooks.sh
#
# Manual run: bash scripts/check_no_wav_commit.sh

set -e

WAV_FILES=$(git diff --cached --name-only --diff-filter=AM | grep -E '^assets/audio/.*\.wav$' || true)

if [ -n "$WAV_FILES" ]; then
    echo "ERROR: Pre-commit guard BLOCKED — staged commit contains assets/audio/*.wav files." >&2
    echo "" >&2
    echo "WAV originals must NOT ship in the repo. They are gitignored." >&2
    echo "If wavs got re-tracked (usually by 'git add -A'), run:" >&2
    echo "" >&2
    echo "    git ls-files 'assets/audio/*.wav' 'assets/audio/**/*.wav' \\" >&2
    echo "        | xargs -d '\\n' -n 200 git rm --cached --quiet" >&2
    echo "    git add -A && git commit ..." >&2
    echo "" >&2
    echo "Wav files staged in this commit:" >&2
    echo "$WAV_FILES" | head -10 | sed 's/^/    /' >&2
    n=$(echo "$WAV_FILES" | wc -l)
    if [ "$n" -gt 10 ]; then
        echo "    ... and $((n - 10)) more" >&2
    fi
    exit 1
fi

# Also catch large non-wav additions (>50 MB single file) that would bloat repo
LARGE=$(git diff --cached --name-only --diff-filter=AM | while read f; do
    if [ -f "$f" ]; then
        sz=$(wc -c < "$f" 2>/dev/null || echo 0)
        if [ "$sz" -gt 52428800 ]; then
            printf '%s\t%s MB\n' "$f" "$((sz / 1048576))"
        fi
    fi
done)

if [ -n "$LARGE" ]; then
    echo "ERROR: Pre-commit guard BLOCKED — staging large file(s) > 50 MB:" >&2
    echo "$LARGE" | sed 's/^/    /' >&2
    echo "" >&2
    echo "Use Git LFS or split / move the file before committing." >&2
    exit 1
fi

exit 0
