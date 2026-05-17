# Snippet Library

## Utilities

- [`get_base_dir`](utilities/get_base_dir.py) (from `app.py:46`) -- Resolve resource base path for both dev and frozen (PyInstaller) modes.
- [`get_user_data_dir`](utilities/get_user_data_dir.py) (from `app.py:74`) -- Writable per-user folder for kid project saves (Lesson 16).
- [`get_state_file`](utilities/get_state_file.py) (from `app.py:81`) -- File-backed mirror of the kid's localStorage. Belt-and-suspenders persistence
- [`get_webview_storage_path`](utilities/get_webview_storage_path.py) (from `app.py:89`) -- Stable storage_path for pywebview's WebView2 user data folder.
- [`step_sandbox_lint`](utilities/step_sandbox_lint.py) (from `build.py:57`) -- v0.7: validate sandbox JSONs before bundling — abort build on any malformed file.
- [`step_distractor_lint`](utilities/step_distractor_lint.py) (from `build.py:67`) -- Block ship if any wrong-answer text repeats > 3 times in one question.
- [`weighted_sample`](utilities/weighted_sample.py) (from `scripts/audio_qa_report.py:183`) -- Acronym-heavy rows get 2x weight, others 1x.
- [`convert_wav_to_ogg`](utilities/convert_wav_to_ogg.py) (from `scripts/compress_audio_ogg.py:56`) -- Encode `src` (wav) → `dst` (ogg/opus). Returns True on success.
- [`dedupe_question`](utilities/dedupe_question.py) (from `scripts/dedupe_distractors.py:89`) -- Rewrite distractor text per-slot so no string repeats > max_repeats times.
- [`diversify_lesson`](utilities/diversify_lesson.py) (from `scripts/diversify_gates.py:168`) -- Rewrite Q2..Qn interactions for one lesson. Q1 untouched.
- [`expand_lesson`](utilities/expand_lesson.py) (from `scripts/expand_lessons_v2.py:1256`) -- Load lesson_NN.json, attach questions[], write back. Returns True on OK.
- [`fix_file`](utilities/fix_file.py) (from `scripts/fix_question_quality.py:103`) -- Replace problematic strings (raw text, not json-escaped — the file stores
- [`celebration_extra`](utilities/celebration_extra.py) (from `scripts/gen_sfx.py:254`) -- Hidden voice clip used as the surprise 'MAMA MIA' celebration moment.
- [`is_available`](utilities/is_available.py) (from `scripts/piper_bake.py:29`) -- True if Piper is importable AND the voice file exists.
- [`synth`](utilities/synth.py) (from `scripts/piper_bake.py:49`) -- Synthesize `text` to `out_path` (WAV). Returns True on success.
- [`make_type_payload`](utilities/make_type_payload.py) (from `scripts/swap_click_to_type.py:60`) -- Build a `type-this-word` interaction payload for a given word.
- [`swap_lesson`](utilities/swap_lesson.py) (from `scripts/swap_click_to_type.py:86`) -- Walk a lesson's questions[] and:

## Classes

- [`AudioRow`](classes/AudioRow.py) (from `scripts/audio_qa_report.py:64`) -- A single auditable audio entry.
- [`Note`](classes/Note.py) (from `scripts/gen_sfx.py:31`)
