# Kids Code Academy — Tutorial
**Last updated:** 2026-05-01 (v0.1.0)

---

## 1. Quickstart

Get a 7-year-old learning to code in under 60 seconds.

1. Double-click `C:\Users\computer\Desktop\AI\KidsCodeAcademy.exe`.
2. The window opens. Bytey the robot waves. The first lesson is already on screen.
3. Click **▶ Play**. Bytey reads the lesson out loud.
4. Click the right answer in the mini-game. Earn a sticker. Move on to Lesson 2.

That's it — no install, no setup, no internet.

## 2. Feature Walkthrough

### Lessons
- **What it does** — 16 short lessons that teach the dev workflow used with Claude, Cursor, Gemini.
- **When to use it** — every day, 5-10 minutes per session.
- **How to do it** — click a lesson card on the left. Listen to the narration (▶ Play). Do the mini-game.
- **Example** — Lesson 1 ("What Is a Computer?") asks "Which one is a computer?" with four choices. Click the laptop.
- **Gotchas** — Lessons 2-7 unlock in order. Lessons 8-15 unlock as a group once Lesson 7 is done.

### The mascot — "Bytey"
- **What it does** — animates, waves, cheers, and thinks based on what's happening on screen.
- **When to use it** — automatic. Click ▶ Play to make Bytey "talk".
- **Gotchas** — the mascot freezes between lessons until Play is pressed.

### Read-aloud
- **What it does** — every lesson has a pre-baked voice clip; click ▶ Play or the **Read aloud** button up top.
- **When to use it** — for any kid who isn't reading fluently yet.
- **Gotchas** — the voice is Windows SAPI Zira. If you'd prefer a different voice, regenerate `assets/audio/` with a different voice and re-run `python build.py --no-package`.

### Mini-games
There are 6 game types woven through the lessons:
- **Click the right one** (Lesson 1, 7, 9, 14)
- **Drag to match** (Lesson 3, 8, 13)
- **Type the word** (Lesson 2, 10)
- **Place the blocks** (Lesson 4, 12)
- **Order the steps** (Lesson 5, 6, 11)
- **Read out loud** (Lesson 15)

### Pretend "Claude / Cursor / Gemini" chat
- **What it does** — Lessons 2 and 8 give the kid a chat box that looks like a real AI helper.
- **When to use it** — kid types a wish ("make me a star"); the helper "replies" and may draw a shape.
- **How to do it** — type up to 80 characters; press **Ask** or Enter.
- **Gotchas** — replies are pre-scripted. The kid can't break it, but they also can't get a unique answer to a unique question. That's intentional.

### Lesson 16 — First Real Project
- **What it does** — kid picks a part of "Bubby's World" (Hero / Ground / Block) and a color, then saves the result.
- **How to do it** — tap a part, tap a color swatch, tap **Save my world**.
- **Result** — an SVG file lands at `C:\Users\<you>\AppData\Roaming\KidsCodeAcademy\kid_projects\bubbys_world_<timestamp>.svg`. Open it in any browser to admire.

### Parent Corner
- **What it does** — PIN-gated dashboard for the parent.
- **How to do it** — click **Parent Corner** in the top-right. Enter PIN (default `1234`). View progress, the kid's typed prompts, and reset progress if needed. Change the PIN inside.
- **Gotcha** — the PIN is stored locally only. If you forget it, click **Reset all progress** from another device or wipe localStorage in the dev tools (right-click → Inspect inside the running app).

## 3. Common Workflows / Recipes

### Recipe: First night with the app
1. Sit next to your kid. Open the EXE.
2. Walk through Lesson 1 together. Read the words; let the kid click.
3. Stop after Lesson 3. Do more tomorrow.
4. Open Parent Corner once they've gone to bed; review what they did.

### Recipe: Add a new lesson without rebuilding
1. Drop a new file at `lessons/lesson_17_<slug>.json` matching the schema in any existing lesson.
2. Add `"lesson_17_<slug>"` to the `LESSON_IDS` array near the top of `index.html`.
3. Write narration: add to `mascot_lines`. Then run `python scripts/prebake_audio.py` to generate the new `assets/audio/lesson_17.wav`.
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
| No voice when clicking ▶ Play | `assets/audio/lesson_NN.wav` missing | `python scripts/prebake_audio.py` then `python build.py` |
| "Couldn't load lessons" message | `lessons/` folder didn't ship | `python build.py` (PyInstaller `--add-data` re-bundles it) |
| Kid wants to redo a lesson | Lessons re-playable but only sticker-counted once | Open Parent Corner → Reset all progress, or re-click the lesson card (it still plays narration + game) |
| Lesson 16 "Save" doesn't seem to do anything | App running from source without pywebview JS bridge active | The save call falls back to "complete the lesson" silently in dev mode; the bundled .exe writes the file |

## 5. FAQ

- **Q: Does it use my internet?** A: No. Everything is local.
- **Q: Will my kid see ads?** A: No. There are none.
- **Q: Can my kid type something inappropriate to "Claude"?** A: Yes — and the helper just replies with the fallback string. We log every typed prompt to the Parent Corner so you can see what they tried.
- **Q: Can it run on macOS / Linux / iPad?** A: v1 ships Windows .exe only. The HTML is platform-neutral, so a future PWA / APK build is straightforward.
- **Q: Is this a real Claude?** A: No, and intentionally so. It's a sandbox that simulates the experience without internet access.

## 6. Changelog (user-facing)

### 2026-05-01 — v0.1.0
- Added: 16 lessons, mascot animation, read-aloud audio, 6 mini-game types, sandbox AI for Lessons 2 + 8, Parent Corner with PIN, Lesson 16 save-a-copy.
- Shipped: `KidsCodeAcademy.exe` (~48 MB) on Windows.

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
