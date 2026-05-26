# Kids Code Academy — Project Rules

Project-local rules that override the parent `CLAUDE.md` for files inside
`C:\Users\computer\Desktop\AI\KidsCodeAcademy\`.

## Audience hard-rules
- **The end user is a 7-year-old.** Every user-visible string must be readable at 2nd-grade level.
- **Read-aloud is always on.** Every new lesson MUST get a `mascot_lines` block + a re-bake of `assets/audio/lesson_NN.wav` via `python scripts/prebake_audio.py`.
- **No PII**. Never store kid's real name, school, address, parent email. localStorage only. No fetch calls outside of `assets/`, `lessons/`, `sandbox_ai/`.
- **No real API calls.** All AI helpers (Claude, Cursor, Gemini) are simulated via `sandbox_ai/<helper>/lesson_NN.json`. Do not add real-AI calls in v1.

## Curriculum hard-rules
- Lessons 1-7 unlock linearly; 8-15 are free-pick after Lesson 7. Lesson 16 is the capstone.
- Each new lesson must add a `lessons/lesson_NN_*.json` file matching the existing schema and re-run `prebake_audio.py`.
- Mini-game `type` must be one of: `click-the-thing`, `drag-to-match`, `type-this-word`, `place-blocks`, `sequence-the-steps`, `guided-talk`. Adding a new type means extending `KidGame._handlers` in `index.html`.

## Code hard-rules
- **Never use `innerHTML`** with caller-supplied strings. Use `el(...)` / `createElement` / `textContent` / `setAttribute` everywhere. Static SVG goes through `svgEl(...)`.
- Validate every value that flows into the DOM from JSON: helper names match `/^[a-z]+$/`, colors pass `isHexOrNamed`, kid input capped at 80 chars per turn.
- Single source of truth for the lesson list is the `LESSON_IDS` constant in `index.html` AND filenames in `lessons/`. Keep them aligned.

## Build hard-rules
- `python build.py` is the only supported build path. Never invoke `pyinstaller` directly.
- Final exe lives at `C:/Users/computer/Desktop/AI/KidsCodeAcademy.exe`. Don't rename.
- Use `uv pip` per global rules. Never `pip`.
- Run `bash ~/.claude/scripts/check-gui-integrity.sh "C:/Users/computer/Desktop/AI/KidsCodeAcademy"` before pushing.

<!-- claude-backend:generated:start -->
# KidsCodeAcademy

## Overview

- **Files**: 120 (.json (78), .py (33), .md (9))
- **Entry points**: `app.py`, `build.py`, `gen_icons.py`, `gen_mascot.py`, `scripts/audio_qa_report.py`
- **Dependencies**: pywebview, pyinstaller, pillow, pyttsx3
- **Key files**: `README.md`, `CLAUDE.md`, `requirements.txt`, `.gitignore`

## Structure

```
lessons/  (60 files)
logs/  (1 files)
sandbox_ai/  (16 files)
  claude/  (11 files)
  codex/  (1 files)
  cursor/  (1 files)
  gemini/  (1 files)
  ollama/  (1 files)
  opencode/  (1 files)
scripts/  (29 files)
vendor/  (2 files)
  snapshot_bubbys_game/  (1 files)
  snapshot_sprite_editor/  (1 files)
voices/  (1 files)
```

## Conventions

- Use `pathlib.Path` for all path operations
- Type hints are used extensively -- maintain them
- Use specific exception types in except clauses
- Absolute imports preferred

## Modules

- `app.py` -- Kids Code Academy — sandboxed coding tutorial for ages 7+ [entry]
- `build.py` -- Build pipeline for Kids Code Academy [entry]
- `gen_icons.py` -- Generate app icons for Kids Code Academy [entry]
- `gen_mascot.py` -- Generate procedural mascot frames for Bytey [entry]
- `scripts/audio_qa_report.py` -- Generate an HTML audio QA report for parent spot-checking [entry]
- `scripts/audit_question_quality.py` -- Audit every question/variation across all lessons for 7-year-old quality [entry]
- `scripts/author_lessons.py` -- Author all v0.3.0 net-new lesson JSONs in one shot
- `scripts/author_scenario_q7.py` -- Rewrite q7 in the 30 lessons that have it from a 2nd "pick the silly one" [entry]
- `scripts/bake_option_audio.py` -- Bake one Piper TTS wav per UNIQUE answer-option text [entry]
- `scripts/bake_q7_audio.py` -- Bake audio for the rewritten q7 scenario questions only [entry]
- `scripts/bake_question_prompts.py` -- Bake one Piper TTS wav per question variation prompt [entry]
- `scripts/check_distractor_dupes.py` -- Audit lesson questions for over-repeated wrong-answer (distractor) text [entry]
- `scripts/compress_audio_ogg.py` -- Compress every WAV in assets/audio/ to OGG/Opus, then rewrite lesson JSON [entry]
- `scripts/dedupe_distractors.py` -- Auto-fix over-repeated wrong-answer distractors across all lesson questions [entry]
- `scripts/diversify_gates.py` -- Diversify Q2+ gate interactions across all 60 lessons [entry]
- `scripts/expand_lessons_v2.py` -- Expand every lesson_NN_*.json into the v2 (questions[] + variations[]) schema [entry]
- `scripts/expand_lessons_v3.py` -- v0.6 lesson expander — much richer + more comedic content per lesson [entry]
- `scripts/fix_duplicate_options.py` -- Fix variations that list the same answer-option text twice [entry]
- `scripts/fix_question_quality.py` -- Replace low-quality / age-inappropriate distractor strings across all lessons [entry]
- `scripts/gen_sfx.py` -- Generate warm, kid-friendly SFX wav files using only stdlib [entry]
- `scripts/lift_q1_games.py` -- Lift Q1 interactions for under-engaging arcs to themed mini-games [entry]
- `scripts/piper_bake.py` -- Piper TTS bake helper
- `scripts/prebake_audio.py` -- Pre-render lesson narration to wav files using pyttsx3 (Windows SAPI) [entry]
- `scripts/preprocess_acronyms.py` -- Re-bake any wav whose source text contains a tech acronym Piper mispronounces [entry]
- `scripts/purge_filler_gates.py` -- Purge filler MCQ gates → type-this-word everywhere they appear [entry]
- `scripts/rebalance_distractors.py` -- Rebalance any wrong-answer that appears more than 3x within a question [entry]
- `scripts/rewrite_mascot_lines.py` -- Rewrite every lesson's mascot_lines into flowing, natural narration [entry]
- `scripts/rewrite_q_openers.py` -- Replace the flat 'What is <title>?' Q1-v0 prompt across all 60 lessons [entry]
- `scripts/sandbox_lint.py` -- Sandbox JSON validator — runs at build time before PyInstaller [entry]
- `scripts/seed_enrichments_v4.py` -- Per-lesson content enrichments for the 5->10 variation expansion
- `scripts/swap_click_to_type.py` -- Swap every `click-the-thing` gate interaction to `type-this-word` [entry]
- `scripts/verify_persistence.py` -- Persistence verification harness [entry]
- `scripts/wire_engines.py` -- Wire v0.3.1 mini-game engines into the relevant lesson JSONs

## Snippets

See `.claude/snippets/INDEX.md` for reusable code blocks.

<!-- claude-backend:generated:end -->
