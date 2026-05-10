# Kids Code Academy — Breakdown
**Created:** 2026-05-01
**Location:** `C:\Users\computer\Desktop\AI\KidsCodeAcademy`
**Language/Stack:** Python 3.11 (pywebview wrapper) + single-file vanilla HTML/CSS/JS, packaged via PyInstaller into a standalone Windows `.exe`.

---

## 1. What It Does
A safe, offline coding tutorial for a 7-year-old. Teaches the same dev workflow the user uses (planning, asking AI helpers, sticky-note rules, verify-before-done) through 16 progressively-harder lessons, each with a cartoon mascot, read-aloud audio, and a mini-game. All "AI" interactions are pre-scripted JSON — zero network, zero API cost, zero risk. Ships as one Windows `.exe` next to the existing `ClaudeCodeMastery.exe`.

## 2. How To Run It
- **Install:** `uv pip install -r requirements.txt`
- **Run from source:** `python app.py`
- **Build the EXE:** `python build.py` (~90s end-to-end including TTS prebake)
  - `python build.py --no-audio` to skip TTS (~30s)
  - `python build.py --no-package` to refresh assets only
- **Ship target:** `C:\Users\computer\Desktop\AI\KidsCodeAcademy.exe` (~48 MB)
- **Requirements:** Windows 10+, Python 3.11. WebView2 runtime ships with Windows 11.

## 3. Architecture & File Structure

```
KidsCodeAcademy/
├── app.py                              # pywebview wrapper + JSBridge for kid_projects save
├── index.html                          # single-file UI, mini-game engine, mascot, sandbox AI, parent corner
├── build.py                            # asset gen → TTS prebake → PyInstaller → publish → clean
├── gen_icons.py                        # Pillow icon + .ico generator (Bytey-themed)
├── gen_mascot.py                       # Pillow procedural mascot frames (24 PNGs)
├── requirements.txt                    # pywebview, pyinstaller, pillow, pyttsx3
├── README.md / TUTORIAL.md / HANDOFF.md / CLAUDE.md
├── icons/        app.ico, icon-{192,512,512-maskable}.png
├── assets/
│   ├── mascot/   {idle,wave,cheer,think}_NN.png       # 8+6+6+4 frames
│   ├── sfx/      {click,ding,level_up,star_award,oops,page_flip,mascot_hi,type_pop}.wav
│   ├── audio/    lesson_01.wav .. lesson_16.wav        # pre-baked TTS narration
│   └── fonts/, bg/                                     # reserved for v2 art
├── lessons/      lesson_NN_*.json                      # 16 lesson manifests
├── sandbox_ai/
│   ├── claude/   lesson_02.json, lesson_08.json
│   ├── cursor/   lesson_08.json
│   └── gemini/   lesson_08.json
├── parent/       parent_corner.html                    # placeholder (live UI inside index.html)
├── scripts/
│   ├── gen_sfx.py                                     # synthesize 8 procedural .wav clips
│   └── prebake_audio.py                               # pyttsx3 SAPI → 16 .wav files
└── vendor/
    ├── snapshot_sprite_editor/                         # reserved
    └── snapshot_bubbys_game/                           # reserved
```

**Data flow:**
1. `app.py` resolves `index.html` (dev path or PyInstaller `_MEIPASS`), creates the pywebview window with a `JSBridge` js_api.
2. `index.html` boots → `LessonStore.load()` fetches each `lessons/*.json` → `UI.renderSidebar()` builds the lesson list with locked / unlocked / completed states.
3. Click a lesson → `UI.openLesson(id)` renders mascot + speech bubble + audio controls + chat (if `lesson.sandbox.helpers`) + game area.
4. Mini-game completion → `UI.completeLesson(id)` writes to `localStorage`, plays sticker SFX, swaps mascot to `cheer`.
5. Lesson 16 saves the kid's edited SVG to `%APPDATA%\KidsCodeAcademy\kid_projects\` via `JSBridge.save_kid_project`.

## 4. Key Decisions & Why
- **Forked the existing `cc-mastery-pwa` engine pattern instead of starting fresh** — same pywebview + single-HTML model the adult app uses. Cuts shipping pipeline rebuild work to zero.
- **All "AI" is pre-scripted JSON, not real API calls** — zero cost, zero risk for a 7-year-old, zero network surface. Future v2 can swap one `Sandbox.load` call for a real client.
- **Procedural mascot via Pillow primitives, not commissioned art** — ships day-1, every frame is reproducible from source, real art swap is a folder drop.
- **TTS pre-baked at build time, not runtime** — pyttsx3 / SAPI is a Python dependency we don't want inside the shipped exe; baking 16 short wavs at build adds ~1s and keeps the exe runtime dependency-free.
- **DOM construction (`el()`/`createElement`) instead of `innerHTML`** — pre-empts XSS even on local-JSON-only paths. Hook-enforced via the workspace's security_reminder hook.
- **Linear unlock for lessons 1-7, free-pick after** — gives kids a clear early progression, then autonomy once concepts are seeded.
- **Kid project saves to `%APPDATA%`, never inside the bundled exe** — bundled paths are read-only post-PyInstaller; AppData is the safe writable location.

## 5. Development Log

### 2026-05-01 — Initial creation
- Built core: pywebview wrapper, single-file `index.html` with kid theme + dark-mode-ready CSS variables.
- Built `KidGame` engine with 6 mini-game types: `click-the-thing`, `drag-to-match`, `type-this-word`, `place-blocks`, `sequence-the-steps`, `guided-talk`.
- Built mascot animation state machine (idle / wave / cheer / think) using procedural Pillow frames.
- Built sandbox AI engine (keyword-match → typewriter reply → optional SVG side-effect).
- Wrote 16 lessons mapping the user's actual workflow (CLAUDE.md sticky notes, plan-first, verify-before-done, three-helpers comparison, untrusted-content rule, tokens-as-snacks, etc.).
- Built Parent Corner with PIN gate, transcript log, progress reset.
- Built Lesson 16 capstone: live color-swap of inline-SVG "Bubby's World" with save-to-AppData.
- Built `gen_sfx.py` (8 procedural .wav files) and `prebake_audio.py` (pyttsx3 SAPI narration for all 16 lessons).
- Built `build.py` pipeline → ships `KidsCodeAcademy.exe` (~48 MB) next to `ClaudeCodeMastery.exe`.
- Verified exe launches, loads `index.html` from PyInstaller `_MEIPASS`.
- Skipped/deferred for v2: real Bytey art, ElevenLabs voice quality, PWA + APK builds, full Sprite Editor / Bubby's Game snapshots in `vendor/`, locale-swap support.
- Known issues: only Lesson 2 + Lesson 8 ship sandbox AI scripts in v1; other lessons can have their `sandbox` block added without code change.

### 2026-05-03 → 2026-05-09 — Catch-up entry (v0.2.0 → v0.7.7)

The architecture sketched above is mostly stable, but the project has grown ~13× by file count + 3× by lesson count. Authoritative session-by-session diffs live in `HANDOFF.md` (top-of-file). High-level deltas vs. the v0.1.0 sketch:

- **Lessons:** 16 → 60. New chapters: AI history (math/Turing/perceptron/training/attention/LLM), helper deep-dives (claude/cursor/gemini/codex/opencode/ollama), prompt-engineering arc, memory arc, game-dev iteration arc, idea-to-game capstone (L60).
- **Schema:** every lesson upgraded to v2 — `questions[] × variations[]` with 4-7 questions per lesson and 5-10 paraphrased variations per question. Total: ~3,900 question prompts. Defeats memorization.
- **Audio:** pyttsx3 SAPI → Piper (`en_US-amy-medium`). All narration + every question prompt + every answer option are pre-baked. Acronym preprocessing (Phase 5) so "LLM" → "L L M". OGG/Opus compression (Phase 4) shrunk audio bundle from 1.2 GB to ~120 MB. v0.7.7 stripped the SAPI fallback — bake fails LOUD if voice missing.
- **Engine additions:** `ToolSimulator` overlay (per-helper themed UI for L11-16), `KidGame` handlers expanded from 6 to 14+ types (game-capstone, world-layers, input-trace, costume-swapper, live-hud, polish-row, cursor-mini, playtest-preview, share-card, tap-the-glow, pick-the-pic, sprite-poke, timeline-order, prompt-grader), `QuestionFlow` controller (gate-then-answer pattern), hover audio on every option, voice mutex (single channel speaks at a time).
- **Chess break:** new module — full board, weak-on-purpose bot, grading w/ stars + letter grade + score, history tracking, 15-min timer + extension, strategic hint button.
- **Parent Corner:** transcripts + Chess tab + Games tab (game launcher + per-lesson option preview).
- **Pi build:** `scripts/build_pi.sh` + `KCA_BAKE_AUDIO` opt-in + `.github/workflows/pi-build.yml` self-hosted runner workflow.
- **Build pipeline:** sandbox lint (step 1b), distractor dedupe lint (step 1c), question prompt bake (step 2c), acronym preprocess (step 2d), OGG compress (step 2e), staged `build_pkg/assets/` (excludes WAVs, ships only OGGs).
- **Pre-commit guard:** rejects WAV re-tracking + 50MB+ files.
- **exe size trajectory:** 48 MB → 81 MB → 89 MB → 165 MB → 445 MB → **134 MB** (post-OGG, current).

For session-grain detail, read `HANDOFF.md` History section.
