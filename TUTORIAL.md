# Kids Code Academy — Tutorial
**Last updated:** 2026-08-26 (v0.9.3)

---

## 1. Quickstart

Get a 7-year-old learning to code in under 60 seconds.

1. Double-click `KidsCodeAcademy.exe` on the Desktop.
2. The window opens. Bytey the robot waves. The first lesson is already on screen.
3. Click **▶ Play**. Bytey reads the lesson out loud.
4. Click the right answer in the mini-game. Earn a sticker. Move on to Lesson 2.

That's it — no install, no setup, no internet.

## 2. Feature Walkthrough

### Lessons
- **What it does** — 60 short lessons across 10 chapters, from computer basics and safe AI habits through prompts, game design, debugging, and a final project.
- **When to use it** — every day, 5-10 minutes per session.
- **How to do it** — click a lesson card on the left. Listen to the narration (▶ Play). Do the mini-game.
- **Example** — Lesson 1 ("What Is a Computer?") asks "Which one is a computer?" with four choices. Click the laptop.
- **Gotchas** — Lessons unlock in order. A parent can set the exact resume lesson or mark a block complete from Parent Corner → Settings.

### The mascot — "Bytey"
- **What it does** — animates, waves, cheers, and thinks based on what's happening on screen.
- **When to use it** — automatic. Click ▶ Play to make Bytey "talk".
- **Gotchas** — the mascot freezes between lessons until Play is pressed.

### Read-aloud
- **What it does** — every lesson has a pre-baked voice clip; click ▶ Play or the **Read aloud** button up top.
- **When to use it** — for any kid who isn't reading fluently yet.
- **Gotchas** — authored narration uses pre-baked Piper OGG clips. Missing clips fall back gracefully; regenerate them with the scripts in `scripts/` before rebuilding.

### Mini-games
Lessons mix quizzes, matching, ordering, typing, block-building, simulated tool conversations, game-design activities, review questions, and a short math minute. Every lesson has three unique math questions across 34 skills. Lessons 1–48 build and master Grade 2 foundations; Lessons 49–60 gently bridge into early Grade 3. **Show me how** reads and displays a strategy, and appears automatically after two wrong tries.

Important coding words also appear in **Word Power** cards with a plain-language definition and speaker button.

### Pretend "Claude / Cursor / Gemini" chat
- **What it does** — Lessons 2 and 8 give the kid a chat box that looks like a real AI helper.
- **When to use it** — kid types a wish ("make me a star"); the helper "replies" and may draw a shape.
- **How to do it** — type up to 80 characters; press **Ask** or Enter.
- **Gotchas** — replies are pre-scripted. The kid can't break it, but they also can't get a unique answer to a unique question. That's intentional.

### Lesson 60 — Make Your Game
- **What it does** — the kid brainstorms an idea, paints a level, names it, and creates a share card.
- **Result** — project JSON and a printable HTML card land in `%APPDATA%\KidsCodeAcademy\kid_projects\` and appear in Parent Corner → Projects.

### Chess break
- **What it does** — offers a friendly 15-minute chess game after the current lesson. It enforces check, checkmate, stalemate, castling, en passant, and promotion, and includes legal-move hints, short piece lessons, a timer, restart, and exit controls.
- **Gotcha** — it is deliberately a beginner-friendly opponent, not a tournament chess engine.

### Parent Corner
- **What it does** — PIN-gated dashboard for progress, transcripts, saved projects, memory rules, accessibility, chess history, and settings.
- **How to do it** — click **Parent Corner** in the top-right. First use asks the parent to create a PIN. In Settings, use **Continue at this lesson** to choose the next lesson without falsely completing it, or **Mark through complete** to award completion through a selected lesson.
- **Gotcha** — the PIN and progress stay on this computer. The desktop app mirrors progress to `%APPDATA%\KidsCodeAcademy\state.json` so a restart does not lose it.

## 3. Common Workflows / Recipes

### Recipe: First night with the app
1. Sit next to your kid. Open the EXE.
2. Walk through Lesson 1 together. Read the words; let the kid click.
3. Stop after Lesson 3. Do more tomorrow.
4. Open Parent Corner once they've gone to bed; review what they did.

### Recipe: Add a new lesson without rebuilding
1. Drop a new numbered JSON file in `lessons/`, matching the schema in an existing lesson.
2. Add its identifier to the `LESSON_IDS` array near the top of `index.html`.
3. Write narration and questions, then run the audio scripts to generate the new OGG clips.
4. `python build.py` to ship a new `.exe`, or just `python app.py` to test.

### Recipe: Change the PIN as a parent
1. Open Parent Corner with current PIN.
2. Type a new 4-digit number into "Change PIN".
3. Click **Save PIN**.

## 4. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| EXE opens then closes immediately | Antivirus quarantined PyInstaller bootloader | Restore from quarantine, or run `python app.py` directly |
| Mascot is a blank rectangle | `assets/mascot/` not bundled | Re-run `python build.py` to regenerate + re-package |
| No voice when clicking ▶ Play | A referenced OGG clip is missing | Run the audio-generation scripts, then `python build.py` |
| "Couldn't load lessons" message | `lessons/` folder didn't ship | `python build.py` (PyInstaller `--add-data` re-bundles it) |
| Kid wants to redo a lesson | Lessons re-playable but only sticker-counted once | Open Parent Corner → Reset all progress, or re-click the lesson card (it still plays narration + game) |
| Lesson 60 "Save" doesn't seem to do anything | App running in a plain browser without the desktop bridge | Use the bundled EXE to write project files |

## 5. FAQ

- **Q: Does it use my internet?** A: No. Everything is local.
- **Q: Will my kid see ads?** A: No. There are none.
- **Q: Can my kid type something inappropriate to "Claude"?** A: Yes — and the helper just replies with the fallback string. We log every typed prompt to the Parent Corner so you can see what they tried.
- **Q: Can it run on macOS / Linux / iPad?** A: v1 ships Windows .exe only. The HTML is platform-neutral, so a future PWA / APK build is straightforward.
- **Q: Is this a real Claude?** A: No, and intentionally so. It's a sandbox that simulates the experience without internet access.

## 6. Changelog (user-facing)

### 2026-08-26 — v0.9.3
- Fixed: every typing activity now clearly displays the exact word or phrase the child needs to enter.
- Added: a high-contrast target card and speaker button that reads the typing example aloud.
- Improved: input labels, placeholders, and retry hints now repeat the target clearly.
- Protected: future builds fail if a typing activity lacks a visible target, accepted answer, or retry hint.

### 2026-08-25 — v0.9.2
- Verified: all 378 historically flagged hard-word locations now use simpler language, a child-friendly compound, or a visible Word Power definition.
- Improved: important coding and AI words remain teachable instead of being removed; every retained technical term has a plain explanation and read-aloud audio.
- Protected: future builds fail if a Word Power definition is missing, too long, uses unexplained jargon, is duplicated, or lacks audio.

### 2026-08-25 — v0.9.1
- Improved: answer choices now keep the meaning of each replay, include a believable misconception, and avoid filler wording and duplicate choices.
- Added: a calm built-in music loop; music remains off by default and automatically quiets under narration.
- Improved: manual progress placement and file-backed progress storage reject corrupt writes instead of replacing good data.
- Improved: keyboard and screen-reader support for lesson navigation, Parent Corner tabs, dialogs, and answer audio buttons.
- Improved: Compact mode now works in half-screen windows down to 560px wide.

### 2026-08-25 — v0.9.0
- Polished: all flagged long prompts, repeated prompt templates, and fragment answers were rewritten and re-recorded.
- Expanded: 180 unique math questions across 34 skills, sequenced from Grade 2 foundations to an early Grade 3 bridge, with visible and read-aloud strategies.
- Added: Word Power cards that explain and read important coding terms aloud.
- Rebuilt: chess now enforces complete legal rules and offers useful legal-move hints plus piece lessons.
- Improved: chess and learning controls fit shorter screens and remain keyboard accessible.

### 2026-08-25 — v0.8.0
- Added: clear parent controls for choosing a resume lesson or marking progress through a lesson.
- Expanded: 180 unique math-minute prompts across 26 skills, with matching read-aloud audio.
- Improved: repeated distractor checks and substantially faster one-file EXE startup.
- Verified: all 60 lessons, chess launch and controls, state persistence, and packaged Windows startup.

### 2026-05-01 — v0.1.0
- Added: 16 lessons, mascot animation, read-aloud audio, 6 mini-game types, sandbox AI for Lessons 2 + 8, Parent Corner with PIN, Lesson 16 save-a-copy.
- Shipped: `KidsCodeAcademy.exe` (~48 MB) on Windows.

### 2026-05-08 (later) — v0.7.1 (every question read aloud in the same warm voice)
- Changed: every question prompt is now pre-baked with the same Piper voice that reads the lessons. No more two-different-voices feel.
- Added: Pi build supports the same Piper voice. Set `KCA_BAKE_AUDIO=1` when running `build_pi.sh` to re-bake on the Pi instead of using the wavs that came with the repo.
- Note: build size grew (~165 MB) because all 1950 question-prompt wavs ship inside the exe.

### 2026-05-08 — v0.7.0 (real-feeling sandbox sims + game-dev tools + warmer voice)
- Added: offline simulations of 6 real helpers your kid can talk to — Claude, Cursor, Gemini, Codex, OpenCode, and Ollama. Each looks and feels close to the real tool. Click "Open [helper]" inside lessons 11-16 to expand the chat panel.
- Added: each helper opens with a friendly "Hi! I'm [helper] — let's go!" voice line.
- Added: hands-on game-dev tools across 9 lessons that used to be MCQ-only — toggling world layers (lesson 32), tracing arrow-key inputs (33), swapping costumes + FPS (34), tapping coins to score (38), polish toggles for shake/particles/sound (41), sending Cursor a feature request and seeing the diff (45), watching a friend's reactions to your demo (47), and making a paper share card for your game (48).
- Added: lesson 60 is now a real "Make Your Game" capstone — three stages: brainstorm your idea, paint a level, name + share it.
- Changed: lesson narration is now baked with **Piper TTS** (`en_US-amy-medium`) instead of pyttsx3 SAPI. Same kid-friendly female voice but much warmer and more natural. Build size grew slightly (~89.6 MB).
- Note: Piper voice file (~63 MB) is gitignored; downloaded by build via `python -m piper.download_voices en_US-amy-medium --download-dir voices`. Build falls back to pyttsx3 if the voice is missing.

### 2026-05-07 — v0.6.0 (comedy + animations + chess break + female voice)
- Added: a 15-minute chess break that pops up after the kid finishes whatever lesson they're on. Bot is intentionally weak (1-in-10 chance of a smart move) so the kid wins often.
- Added: animated celebration on every right answer. Pick the rocket → it flies off the screen. Pick the star → it spins and grows. Confetti bursts from the chosen item.
- Added: animated stories for lessons 11-16. Watching Claude reply, Cursor type, Gemini look at words AND pictures, Codex auto-complete, OpenCode share with friends, Ollama work without wifi.
- Changed: question reading voice is now a friendly female voice (was a male voice some kids didn't like). Cached on first session start.
- Changed: lesson questions are MUCH more varied + funnier. Each lesson now has 8 hand-written silly wrong-answers + 2 scenario questions (e.g., "Bytey wants to bake a cake but he's just words. What can a real computer do to help?"). 8 question frames mix factual + comedic angles so the kid can't anchor on one shape.

### 2026-05-07 — v0.5.0 (anti-memorization + interaction gating)
- Added: 4-7 multiple-choice questions per lesson (was 1), each with 5 randomly-picked wording variations.
- Added: answer choices stay hidden until the kid completes the demonstration interaction. Speed-clicking through guesses no longer works.
- Added: option positions shuffle every render — kid can't memorize "always the second one".
- Added: question prompts read aloud via Web Speech (no per-question wav files needed).
- Note: kids who already completed a lesson under v0.3.5 still keep their sticker; the lesson now plays the new multi-question flow when re-opened.
