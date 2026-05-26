# Snippet Library

## Utilities

- [`get_base_dir`](utilities/get_base_dir.py) (from `app.py:46`) -- Resolve resource base path for both dev and frozen (PyInstaller) modes.
- [`_appdata_root`](utilities/_appdata_root.py) (from `app.py:53`) -- Stable per-user app data root.
- [`get_user_data_dir`](utilities/get_user_data_dir.py) (from `app.py:74`) -- Writable per-user folder for kid project saves (Lesson 16).
- [`get_state_file`](utilities/get_state_file.py) (from `app.py:81`) -- File-backed mirror of the kid's localStorage. Belt-and-suspenders persistence
- [`get_webview_storage_path`](utilities/get_webview_storage_path.py) (from `app.py:89`) -- Stable storage_path for pywebview's WebView2 user data folder.
- [`_start_local_http_server`](utilities/_start_local_http_server.py) (from `app.py:427`) -- Spin up a tiny loopback HTTP server pointed at serve_dir; return the
- [`_parse_headless_quit_secs`](utilities/_parse_headless_quit_secs.py) (from `app.py:470`) -- Return KCA_HEADLESS_QUIT_SECS as a positive int, or 0 if unset/invalid.
- [`_schedule_headless_close`](utilities/_schedule_headless_close.py) (from `app.py:487`) -- Background-thread function passed to webview.start().
- [`save_state`](utilities/save_state.py) (from `app.py:193`) -- Atomically write state.json. JS calls this on every progress update.
- [`load_state`](utilities/load_state.py) (from `app.py:216`) -- Return state.json contents as a string (empty if no file).
- [`clear_state`](utilities/clear_state.py) (from `app.py:235`) -- Delete state.json. Called only on explicit Reset all progress.
- [`pick_music_file`](utilities/pick_music_file.py) (from `app.py:252`) -- Open a native file picker; copy the chosen audio into AppData as
- [`get_user_music`](utilities/get_user_music.py) (from `app.py:299`) -- Return the parent's saved track as a base64 data URL, or '' if none.
- [`list_kid_projects`](utilities/list_kid_projects.py) (from `app.py:327`) -- v0.7.11 Fix 10: enumerate saved capstone JSON projects.
- [`step_sandbox_lint`](utilities/step_sandbox_lint.py) (from `build.py:57`) -- v0.7: validate sandbox JSONs before bundling — abort build on any malformed file.
- [`step_distractor_lint`](utilities/step_distractor_lint.py) (from `build.py:67`) -- Block ship if any wrong-answer text repeats > 3 times in one question.
- [`_build_audio_pkg`](utilities/_build_audio_pkg.py) (from `build.py:109`) -- Phase 4: build a temp copy of `assets/` that EXCLUDES *.wav so PyInstaller
- [`_emit_option_rows`](utilities/_emit_option_rows.py) (from `scripts/audio_qa_report.py:127`) -- Dedup options by audio path — same audio file may back many lessons.
- [`weighted_sample`](utilities/weighted_sample.py) (from `scripts/audio_qa_report.py:183`) -- Acronym-heavy rows get 2x weight, others 1x.
- [`_hash_text`](utilities/_hash_text.py) (from `scripts/bake_option_audio.py:38`) -- Stable short hash for a text string. 10 hex chars = 1.1T distinct
- [`bake_one`](utilities/bake_one.py) (from `scripts/bake_q7_audio.py:35`) -- Bake `text` to ROOT/ogg_rel. Returns 'baked' | 'skip' | 'fail'.
- [`_audio_relpath`](utilities/_audio_relpath.py) (from `scripts/bake_question_prompts.py:34`) -- Stable relative path used by both bake + runtime.
- [`convert_wav_to_ogg`](utilities/convert_wav_to_ogg.py) (from `scripts/compress_audio_ogg.py:56`) -- Encode `src` (wav) → `dst` (ogg/opus). Returns True on success.
- [`_unique_distractors_in_question`](utilities/_unique_distractors_in_question.py) (from `scripts/dedupe_distractors.py:30`) -- All unique non-empty wrong-answer strings across this question's variations.
- [`_expand_pool`](utilities/_expand_pool.py) (from `scripts/dedupe_distractors.py:57`) -- Pad the unique distractor pool by adding stylistic variants of existing
- [`dedupe_question`](utilities/dedupe_question.py) (from `scripts/dedupe_distractors.py:89`) -- Rewrite distractor text per-slot so no string repeats > max_repeats times.
- [`_word_for`](utilities/_word_for.py) (from `scripts/diversify_gates.py:110`) -- Pull a kid-safe word from the existing swap_click_to_type pool.
- [`_make_payload`](utilities/_make_payload.py) (from `scripts/diversify_gates.py:118`) -- Build a fresh interaction payload for `gate_type`. Returns None if the
- [`diversify_lesson`](utilities/diversify_lesson.py) (from `scripts/diversify_gates.py:166`) -- Rewrite Q2..Qn interactions for one lesson. Q1 untouched.
- [`_build_variation`](utilities/_build_variation.py) (from `scripts/expand_lessons_v2.py:1104`) -- One {prompt, options:[{text,correct}]*4} entry.
- [`expand_lesson`](utilities/expand_lesson.py) (from `scripts/expand_lessons_v2.py:1256`) -- Load lesson_NN.json, attach questions[], write back. Returns True on OK.
- [`_assert_no_dupes`](utilities/_assert_no_dupes.py) (from `scripts/expand_lessons_v3.py:2219`) -- Fail loud if two variations share the same prompt OR same correct text.
- [`_scenario_to_variations`](utilities/_scenario_to_variations.py) (from `scripts/expand_lessons_v3.py:2243`) -- Convert ONE hand-written scenario into VARIATIONS_PER_QUESTION variations.
- [`_gate`](utilities/_gate.py) (from `scripts/expand_lessons_v3.py:2264`) -- Type-this-word gate template — every gate teaches typing across the curriculum.
- [`_question_count`](utilities/_question_count.py) (from `scripts/expand_lessons_v3.py:2285`) -- 5-8 questions per lesson, deterministic from id.
- [`wrong_pool`](utilities/wrong_pool.py) (from `scripts/fix_duplicate_options.py:24`) -- All distinct wrong-option dicts used anywhere in this question.
- [`fix_file`](utilities/fix_file.py) (from `scripts/fix_question_quality.py:103`) -- Replace problematic strings (raw text, not json-escaped — the file stores
- [`_adsr`](utilities/_adsr.py) (from `scripts/gen_sfx.py:38`) -- Smooth ADSR. Linear attack, exponential release. Sustain at 1.0.
- [`_harmonic_voice`](utilities/_harmonic_voice.py) (from `scripts/gen_sfx.py:52`) -- Fundamental + lower 2nd partial + tiny 4th partial.
- [`_soft_saturate`](utilities/_soft_saturate.py) (from `scripts/gen_sfx.py:65`) -- tanh-based soft clip. drive < 1.0 = transparent, > 1.0 = warmer.
- [`_lowpass`](utilities/_lowpass.py) (from `scripts/gen_sfx.py:70`) -- 1-pole IIR low-pass: y[n] = a*x[n] + (1-a)*y[n-1].
- [`_synth_notes`](utilities/_synth_notes.py) (from `scripts/gen_sfx.py:84`) -- Render a sequence of notes through the warm-synth pipeline.
- [`celebration_extra`](utilities/celebration_extra.py) (from `scripts/gen_sfx.py:254`) -- Hidden voice clip used as the surprise 'MAMA MIA' celebration moment.
- [`is_available`](utilities/is_available.py) (from `scripts/piper_bake.py:29`) -- True if Piper is importable AND the voice file exists.
- [`synth`](utilities/synth.py) (from `scripts/piper_bake.py:49`) -- Synthesize `text` to `out_path` (WAV). Returns True on success.
- [`_piper_synth_all`](utilities/_piper_synth_all.py) (from `scripts/prebake_audio.py:47`) -- v0.7: bake every job via Piper TTS instead of pyttsx3 SAPI.
- [`_post_process`](utilities/_post_process.py) (from `scripts/prebake_audio.py:67`) -- Read SAPI wav, add leading silence + low-pass + slight gain, write final wav.
- [`_collect_hint_jobs`](utilities/_collect_hint_jobs.py) (from `scripts/prebake_audio.py:116`) -- Return list of (raw_filename, text) for tier 2 + tier 3 hint narrations.
- [`_spell`](utilities/_spell.py) (from `scripts/preprocess_acronyms.py:67`) -- Replace each acronym match with its spelled-out form. Returns (new_text, hits).
- [`process_lesson`](utilities/process_lesson.py) (from `scripts/purge_filler_gates.py:69`) -- Return per-lesson stats: { q_swaps, game_swap, lesson_id }.
- [`_topic_for`](utilities/_topic_for.py) (from `scripts/rewrite_q_openers.py:41`) -- Strip leading articles + lower-case for natural insertion in the opener.
- [`make_type_payload`](utilities/make_type_payload.py) (from `scripts/swap_click_to_type.py:60`) -- Build a `type-this-word` interaction payload for a given word.
- [`_pool_for`](utilities/_pool_for.py) (from `scripts/swap_click_to_type.py:81`) -- L01-L04 use the clean pool; everyone else gets the full WORDS pool.
- [`swap_lesson`](utilities/swap_lesson.py) (from `scripts/swap_click_to_type.py:86`) -- Walk a lesson's questions[] and:
- [`_appdata_root`](utilities/scripts___appdata_root.py) (from `scripts/verify_persistence.py:45`) -- Cross-platform per-user app data dir — mirrors app.py's _appdata_root().
- [`_default_exe_path`](utilities/_default_exe_path.py) (from `scripts/verify_persistence.py:58`) -- Where build.py's publish step puts the binary, per platform.
- [`_build_fixture`](utilities/_build_fixture.py) (from `scripts/verify_persistence.py:77`) -- Build the fixture state.json contents.
- [`_kill_exe`](utilities/_kill_exe.py) (from `scripts/verify_persistence.py:140`) -- Force-kill any running instance of the EXE.
- [`_check_state`](utilities/_check_state.py) (from `scripts/verify_persistence.py:176`) -- Return (ok, reason).

## Classes

- [`_Handler`](classes/_Handler.py) (from `app.py:444`)
- [`AudioRow`](classes/AudioRow.py) (from `scripts/audio_qa_report.py:64`) -- A single auditable audio entry.
- [`Note`](classes/Note.py) (from `scripts/gen_sfx.py:31`)

## Patterns

- [`save_kid_project`](patterns/save_kid_project.py) (from `app.py:181`)
- [`_load_font`](patterns/_load_font.py) (from `gen_icons.py:27`)
- [`build_variations`](patterns/build_variations.py) (from `scripts/author_scenario_q7.py:204`)
- [`_build_questions`](patterns/_build_questions.py) (from `scripts/expand_lessons_v2.py:1221`)
- [`_build_variation`](patterns/_build_variation.py) (from `scripts/expand_lessons_v3.py:2200`)
- [`_save`](patterns/_save.py) (from `scripts/gen_sfx.py:119`)
- [`_make_typing_payload`](patterns/_make_typing_payload.py) (from `scripts/purge_filler_gates.py:62`)
