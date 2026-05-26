---
name: KidsCodeAcademy Architecture
description: Module map and dependency graph for KidsCodeAcademy
type: reference
---

# KidsCodeAcademy Architecture

## (root)/

- `app.py`: Kids Code Academy — sandboxed coding tutorial for ages 7+. | exports: log, APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WIDTH, MIN_HEIGHT, HTML_FILENAME, get_base_dir
- `build.py`: Build pipeline for Kids Code Academy. | exports: log, ROOT, PROJECT_NAME, ENTRYPOINT, run, step_assets, step_sandbox_lint, step_distractor_lint
- `gen_icons.py`: Generate app icons for Kids Code Academy. | exports: BG_TOP, BG_BOT, BODY, EYE, EYE_SHINE, HEART, TEXT_COLOR, ICONS_DIR
- `gen_mascot.py`: Generate procedural mascot frames for Bytey. | exports: OUT_DIR, SIZE, BODY, BODY_DARK, EYE, EYE_SHINE, HEART, ANTENNA_TIP

## scripts/

- `scripts/audio_qa_report.py`: Generate an HTML audio QA report for parent spot-checking. | exports: log, ROOT, LESSONS_DIR, ASSETS_AUDIO, QA_DIR, ACRONYM_RE, AudioRow, collect_rows
- `scripts/audit_question_quality.py`: Audit every question/variation across all lessons for 7-year-old quality. | exports: ROOT, LESSONS_DIR, REPORT, PROMPT_MAX, HARD_WORD_MIN, JARGON, SILLY, TEMPLATE_OPENERS
- `scripts/author_lessons.py`: Author all v0.3.0 net-new lesson JSONs in one shot. | exports: log, ROOT, LESSONS, write
- `scripts/author_scenario_q7.py`: Rewrite q7 in the 30 lessons that have it from a 2nd "pick the silly one" | exports: log, ROOT, LESSONS_DIR, OPENERS, build_variations, main
- `scripts/bake_option_audio.py`: Bake one Piper TTS wav per UNIQUE answer-option text. | exports: log, ROOT, LESSONS_DIR, OUT_DIR, main
- `scripts/bake_q7_audio.py`: Bake audio for the rewritten q7 scenario questions only. | exports: log, ROOT, LESSONS_DIR, bake_one, main
- `scripts/bake_question_prompts.py`: Bake one Piper TTS wav per question variation prompt. | exports: log, ROOT, LESSONS_DIR, OUT_DIR, main
- `scripts/check_distractor_dupes.py`: Audit lesson questions for over-repeated wrong-answer (distractor) text. | exports: log, ROOT, LESSONS_DIR, main
- `scripts/compress_audio_ogg.py`: Compress every WAV in assets/audio/ to OGG/Opus, then rewrite lesson JSON | exports: log, ROOT, LESSONS_DIR, AUDIO_DIR, OPUS_BITRATE, convert_wav_to_ogg, main
- `scripts/dedupe_distractors.py`: Auto-fix over-repeated wrong-answer distractors across all lesson questions. | exports: log, ROOT, LESSONS_DIR, dedupe_question, main
- `scripts/diversify_gates.py`: Diversify Q2+ gate interactions across all 60 lessons. | exports: log, ROOT, LESSONS_DIR, diversify_lesson, main
- `scripts/expand_lessons_v2.py`: Expand every lesson_NN_*.json into the v2 (questions[] + variations[]) schema. | exports: log, ROOT, LESSONS_DIR, expand_lesson, main
- `scripts/expand_lessons_v3.py`: v0.6 lesson expander — much richer + more comedic content per lesson. | exports: log, ROOT, LESSONS_DIR, VARIATIONS_PER_QUESTION, expand_lesson, main
- `scripts/fix_duplicate_options.py`: Fix variations that list the same answer-option text twice. | exports: log, ROOT, LESSONS_DIR, wrong_pool, fix_variation, main
- `scripts/fix_question_quality.py`: Replace low-quality / age-inappropriate distractor strings across all lessons. | exports: ROOT, LESSONS_DIR, REPLACEMENTS, fix_file, main
- `scripts/gen_sfx.py`: Generate warm, kid-friendly SFX wav files using only stdlib. | exports: log, OUT, Note, click, ding, level_up, star_award, oops
- `scripts/lift_q1_games.py`: Lift Q1 interactions for under-engaging arcs to themed mini-games. | exports: log, ROOT, LESSONS_DIR, main
- `scripts/piper_bake.py`: Piper TTS bake helper. | exports: log, ROOT, VOICES_DIR, DEFAULT_VOICE, is_available, synth
- `scripts/prebake_audio.py`: Pre-render lesson narration to wav files using pyttsx3 (Windows SAPI). | exports: log, ROOT, LESSONS_DIR, OUT_DIR, RAW_DIR, RATE_WPM, LEADING_SILENCE_MS, LPF_CUTOFF_HZ
- `scripts/preprocess_acronyms.py`: Re-bake any wav whose source text contains a tech acronym Piper mispronounces. | exports: log, ROOT, LESSONS_DIR, OPT_DIR, Q_DIR, ACRONYM_RE, main
- `scripts/purge_filler_gates.py`: Purge filler MCQ gates → type-this-word everywhere they appear. | exports: log, ROOT, LESSONS_DIR, process_lesson, main
- `scripts/rebalance_distractors.py`: Rebalance any wrong-answer that appears more than 3x within a question. | exports: log, ROOT, LESSONS_DIR, MAX_REPEATS, wrong_pool, counts, rebalance_question, main
- `scripts/rewrite_mascot_lines.py`: Rewrite every lesson's mascot_lines into flowing, natural narration. | exports: log, ROOT, LESSONS_DIR, main
- `scripts/rewrite_q_openers.py`: Replace the flat 'What is <title>?' Q1-v0 prompt across all 60 lessons. | exports: log, ROOT, LESSONS_DIR, main
- `scripts/sandbox_lint.py`: Sandbox JSON validator — runs at build time before PyInstaller. | exports: ROOT, SANDBOX_DIR, HELPER_RE, ALLOWED_ACTIONS, ALLOWED_PICTURE_IDS, LintError, lint_file, main
- `scripts/seed_enrichments_v4.py`: Per-lesson content enrichments for the 5->10 variation expansion.
- `scripts/swap_click_to_type.py`: Swap every `click-the-thing` gate interaction to `type-this-word`. | exports: ROOT, LESSONS_DIR, make_type_payload, swap_lesson, main
- `scripts/verify_persistence.py`: Persistence verification harness. | exports: log, STATE_FILE, BACKUP_FILE, EXE_PATH, EXE_NAME, MARKER_KEY, MARKER_VALUE, BOOT_WAIT_SECS
- `scripts/wire_engines.py`: Wire v0.3.1 mini-game engines into the relevant lesson JSONs. | exports: log, ROOT, LESSONS, patch
