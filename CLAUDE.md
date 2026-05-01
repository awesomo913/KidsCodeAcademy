# CC Kids Academy — Project Rules

Project-local rules that override the parent `CLAUDE.md` for files inside
`C:\Users\computer\Desktop\AI\cc-kids-academy\`.

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
- Final exe lives at `C:/Users/computer/Desktop/AI/CC-Kids-Academy.exe`. Don't rename.
- Use `uv pip` per global rules. Never `pip`.
- Run `bash ~/.claude/scripts/check-gui-integrity.sh "C:/Users/computer/Desktop/AI/cc-kids-academy"` before pushing.
