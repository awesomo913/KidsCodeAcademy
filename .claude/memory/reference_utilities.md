---
name: KidsCodeAcademy Utilities
description: Reusable functions and their locations in KidsCodeAcademy
type: reference
---

# Reusable Functions in KidsCodeAcademy

| Function | Module | Purpose |
|----------|--------|---------|
| `log` | `app.py` | -- |
| `APP_TITLE` | `app.py` | -- |
| `WINDOW_WIDTH` | `app.py` | -- |
| `WINDOW_HEIGHT` | `app.py` | -- |
| `MIN_WIDTH` | `app.py` | -- |
| `MIN_HEIGHT` | `app.py` | -- |
| `HTML_FILENAME` | `app.py` | -- |
| `get_base_dir` | `app.py` | Resolve resource base path for both dev and frozen (PyInstaller) modes. |
| `get_user_data_dir` | `app.py` | Writable per-user folder for kid project saves (Lesson 16). |
| `get_state_file` | `app.py` | File-backed mirror of the kid's localStorage. Belt-and-suspenders persistence |
| `log` | `build.py` | -- |
| `ROOT` | `build.py` | -- |
| `PROJECT_NAME` | `build.py` | -- |
| `ENTRYPOINT` | `build.py` | -- |
| `run` | `build.py` | -- |
| `step_assets` | `build.py` | -- |
| `step_sandbox_lint` | `build.py` | v0.7: validate sandbox JSONs before bundling — abort build on any malformed file. |
| `step_distractor_lint` | `build.py` | Block ship if any wrong-answer text repeats > 3 times in one question. |
| `step_audio` | `build.py` | -- |
| `step_package` | `build.py` | -- |
| `BG_TOP` | `gen_icons.py` | -- |
| `BG_BOT` | `gen_icons.py` | -- |
| `BODY` | `gen_icons.py` | -- |
| `EYE` | `gen_icons.py` | -- |
| `EYE_SHINE` | `gen_icons.py` | -- |
| `HEART` | `gen_icons.py` | -- |
| `TEXT_COLOR` | `gen_icons.py` | -- |
| `ICONS_DIR` | `gen_icons.py` | -- |
| `main` | `gen_icons.py` | -- |
| `OUT_DIR` | `gen_mascot.py` | -- |
| `SIZE` | `gen_mascot.py` | -- |
| `BODY` | `gen_mascot.py` | -- |
| `BODY_DARK` | `gen_mascot.py` | -- |
| `EYE` | `gen_mascot.py` | -- |
| `EYE_SHINE` | `gen_mascot.py` | -- |
| `HEART` | `gen_mascot.py` | -- |
| `ANTENNA_TIP` | `gen_mascot.py` | -- |
| `SHADOW` | `gen_mascot.py` | -- |
| `BUBBLE` | `gen_mascot.py` | -- |
| `log` | `scripts/audio_qa_report.py` | -- |
| `ROOT` | `scripts/audio_qa_report.py` | -- |
| `LESSONS_DIR` | `scripts/audio_qa_report.py` | -- |
| `ASSETS_AUDIO` | `scripts/audio_qa_report.py` | -- |
| `QA_DIR` | `scripts/audio_qa_report.py` | -- |
| `ACRONYM_RE` | `scripts/audio_qa_report.py` | -- |
| `AudioRow` | `scripts/audio_qa_report.py` | A single auditable audio entry. |
| `collect_rows` | `scripts/audio_qa_report.py` | -- |
| `weighted_sample` | `scripts/audio_qa_report.py` | Acronym-heavy rows get 2x weight, others 1x. |
| `render_html` | `scripts/audio_qa_report.py` | -- |
| `log` | `scripts/author_lessons.py` | -- |
| `ROOT` | `scripts/author_lessons.py` | -- |
| `LESSONS` | `scripts/author_lessons.py` | -- |
| `write` | `scripts/author_lessons.py` | -- |
| `log` | `scripts/bake_option_audio.py` | -- |
| `ROOT` | `scripts/bake_option_audio.py` | -- |
| `LESSONS_DIR` | `scripts/bake_option_audio.py` | -- |
| `OUT_DIR` | `scripts/bake_option_audio.py` | -- |
| `main` | `scripts/bake_option_audio.py` | -- |
| `log` | `scripts/bake_question_prompts.py` | -- |
| `ROOT` | `scripts/bake_question_prompts.py` | -- |
| `LESSONS_DIR` | `scripts/bake_question_prompts.py` | -- |
| `OUT_DIR` | `scripts/bake_question_prompts.py` | -- |
| `main` | `scripts/bake_question_prompts.py` | -- |
| `log` | `scripts/check_distractor_dupes.py` | -- |
| `ROOT` | `scripts/check_distractor_dupes.py` | -- |
| `LESSONS_DIR` | `scripts/check_distractor_dupes.py` | -- |
| `main` | `scripts/check_distractor_dupes.py` | -- |
| `log` | `scripts/compress_audio_ogg.py` | -- |
| `ROOT` | `scripts/compress_audio_ogg.py` | -- |
| `LESSONS_DIR` | `scripts/compress_audio_ogg.py` | -- |
| `AUDIO_DIR` | `scripts/compress_audio_ogg.py` | -- |
| `OPUS_BITRATE` | `scripts/compress_audio_ogg.py` | -- |
| `convert_wav_to_ogg` | `scripts/compress_audio_ogg.py` | Encode `src` (wav) → `dst` (ogg/opus). Returns True on success. |
| `main` | `scripts/compress_audio_ogg.py` | -- |
| `log` | `scripts/dedupe_distractors.py` | -- |
| `ROOT` | `scripts/dedupe_distractors.py` | -- |
| `LESSONS_DIR` | `scripts/dedupe_distractors.py` | -- |
| `dedupe_question` | `scripts/dedupe_distractors.py` | Rewrite distractor text per-slot so no string repeats > max_repeats times. |
| `main` | `scripts/dedupe_distractors.py` | -- |
| `log` | `scripts/diversify_gates.py` | -- |
| `ROOT` | `scripts/diversify_gates.py` | -- |
| `LESSONS_DIR` | `scripts/diversify_gates.py` | -- |
| `diversify_lesson` | `scripts/diversify_gates.py` | Rewrite Q2..Qn interactions for one lesson. Q1 untouched. |
| `main` | `scripts/diversify_gates.py` | -- |
| `log` | `scripts/expand_lessons_v2.py` | -- |
| `ROOT` | `scripts/expand_lessons_v2.py` | -- |
| `LESSONS_DIR` | `scripts/expand_lessons_v2.py` | -- |
| `expand_lesson` | `scripts/expand_lessons_v2.py` | Load lesson_NN.json, attach questions[], write back. Returns True on OK. |
| `main` | `scripts/expand_lessons_v2.py` | -- |
| `log` | `scripts/expand_lessons_v3.py` | -- |
| `ROOT` | `scripts/expand_lessons_v3.py` | -- |
| `LESSONS_DIR` | `scripts/expand_lessons_v3.py` | -- |
| `VARIATIONS_PER_QUESTION` | `scripts/expand_lessons_v3.py` | -- |
| `expand_lesson` | `scripts/expand_lessons_v3.py` | -- |
| `main` | `scripts/expand_lessons_v3.py` | -- |
| `ROOT` | `scripts/fix_question_quality.py` | -- |
| `LESSONS_DIR` | `scripts/fix_question_quality.py` | -- |
| `REPLACEMENTS` | `scripts/fix_question_quality.py` | -- |
| `fix_file` | `scripts/fix_question_quality.py` | Replace problematic strings (raw text, not json-escaped — the file stores |
| `main` | `scripts/fix_question_quality.py` | -- |
| `log` | `scripts/gen_sfx.py` | -- |
| `OUT` | `scripts/gen_sfx.py` | -- |
| `Note` | `scripts/gen_sfx.py` | -- |
| `click` | `scripts/gen_sfx.py` | -- |
| `ding` | `scripts/gen_sfx.py` | -- |
| `level_up` | `scripts/gen_sfx.py` | -- |
| `star_award` | `scripts/gen_sfx.py` | -- |
| `oops` | `scripts/gen_sfx.py` | -- |
| `page_flip` | `scripts/gen_sfx.py` | -- |
| `mascot_hi` | `scripts/gen_sfx.py` | -- |
| `log` | `scripts/lift_q1_games.py` | -- |
| `ROOT` | `scripts/lift_q1_games.py` | -- |
| `LESSONS_DIR` | `scripts/lift_q1_games.py` | -- |
| `main` | `scripts/lift_q1_games.py` | -- |
| `log` | `scripts/piper_bake.py` | -- |
| `ROOT` | `scripts/piper_bake.py` | -- |
| `VOICES_DIR` | `scripts/piper_bake.py` | -- |
| `DEFAULT_VOICE` | `scripts/piper_bake.py` | -- |
| `is_available` | `scripts/piper_bake.py` | True if Piper is importable AND the voice file exists. |
| `synth` | `scripts/piper_bake.py` | Synthesize `text` to `out_path` (WAV). Returns True on success. |
| `log` | `scripts/prebake_audio.py` | -- |
| `ROOT` | `scripts/prebake_audio.py` | -- |
| `LESSONS_DIR` | `scripts/prebake_audio.py` | -- |
| `OUT_DIR` | `scripts/prebake_audio.py` | -- |
| `RAW_DIR` | `scripts/prebake_audio.py` | -- |
| `RATE_WPM` | `scripts/prebake_audio.py` | -- |
| `LEADING_SILENCE_MS` | `scripts/prebake_audio.py` | -- |
| `LPF_CUTOFF_HZ` | `scripts/prebake_audio.py` | -- |
| `POST_GAIN` | `scripts/prebake_audio.py` | -- |
| `main` | `scripts/prebake_audio.py` | -- |
| `log` | `scripts/preprocess_acronyms.py` | -- |
| `ROOT` | `scripts/preprocess_acronyms.py` | -- |
| `LESSONS_DIR` | `scripts/preprocess_acronyms.py` | -- |
| `OPT_DIR` | `scripts/preprocess_acronyms.py` | -- |
| `Q_DIR` | `scripts/preprocess_acronyms.py` | -- |
| `ACRONYM_RE` | `scripts/preprocess_acronyms.py` | -- |
| `main` | `scripts/preprocess_acronyms.py` | -- |
| `log` | `scripts/rewrite_mascot_lines.py` | -- |
| `ROOT` | `scripts/rewrite_mascot_lines.py` | -- |
| `LESSONS_DIR` | `scripts/rewrite_mascot_lines.py` | -- |
| `main` | `scripts/rewrite_mascot_lines.py` | -- |
| `log` | `scripts/rewrite_q_openers.py` | -- |
| `ROOT` | `scripts/rewrite_q_openers.py` | -- |
| `LESSONS_DIR` | `scripts/rewrite_q_openers.py` | -- |
| `main` | `scripts/rewrite_q_openers.py` | -- |
| `ROOT` | `scripts/sandbox_lint.py` | -- |
| `SANDBOX_DIR` | `scripts/sandbox_lint.py` | -- |
| `HELPER_RE` | `scripts/sandbox_lint.py` | -- |
| `ALLOWED_ACTIONS` | `scripts/sandbox_lint.py` | -- |
| `ALLOWED_PICTURE_IDS` | `scripts/sandbox_lint.py` | -- |
| `LintError` | `scripts/sandbox_lint.py` | -- |
| `lint_file` | `scripts/sandbox_lint.py` | Return a list of error strings (empty list = clean). |
| `main` | `scripts/sandbox_lint.py` | -- |
| `ROOT` | `scripts/swap_click_to_type.py` | -- |
| `LESSONS_DIR` | `scripts/swap_click_to_type.py` | -- |
| `make_type_payload` | `scripts/swap_click_to_type.py` | Build a `type-this-word` interaction payload for a given word. |
| `swap_lesson` | `scripts/swap_click_to_type.py` | Walk a lesson's questions[] and: |
| `main` | `scripts/swap_click_to_type.py` | -- |
| `log` | `scripts/verify_persistence.py` | -- |
| `STATE_FILE` | `scripts/verify_persistence.py` | -- |
| `BACKUP_FILE` | `scripts/verify_persistence.py` | -- |
| `EXE_PATH` | `scripts/verify_persistence.py` | -- |
| `EXE_NAME` | `scripts/verify_persistence.py` | -- |
| `MARKER_KEY` | `scripts/verify_persistence.py` | -- |
| `MARKER_VALUE` | `scripts/verify_persistence.py` | -- |
| `BOOT_WAIT_SECS` | `scripts/verify_persistence.py` | -- |
| `main` | `scripts/verify_persistence.py` | -- |
| `log` | `scripts/wire_engines.py` | -- |
| `ROOT` | `scripts/wire_engines.py` | -- |
| `LESSONS` | `scripts/wire_engines.py` | -- |
| `patch` | `scripts/wire_engines.py` | -- |
