# Kids Code Academy

A safe, offline coding tutorial for ages 7+. Teaches the same workflow grown-ups use with Claude, Cursor, and Gemini — but with a cartoon robot mascot, read-aloud audio, and mini-games instead of walls of text.

## Install (Windows)

1. Double-click `KidsCodeAcademy.exe`. That's it.

The exe sits at `C:\Users\computer\Desktop\AI\KidsCodeAcademy.exe`.

## What's inside

- 16 lessons, ages 7+
- Cartoon robot mascot ("Bytey") that animates, waves, cheers, thinks
- 6 mini-game types (drag, click, type, place blocks, sequence, read-aloud)
- Pretend "Claude / Cursor / Gemini" chat — pre-scripted replies, **no internet, no API keys, no cost**
- Sticker rewards + progress saved on the computer
- Parent Corner — PIN-gated panel showing what your kid did and which words they typed

## Safety

- **Zero network**. The app never talks to the internet.
- **No personal info collected**. Progress lives in the browser's localStorage inside the app.
- **PIN-gated parent panel** (default `1234`, changeable inside).
- Lesson 16 saves the kid's project to `%APPDATA%\KidsCodeAcademy\kid_projects\` — nowhere else.

## Develop

```
uv pip install -r requirements.txt
python build.py             # full build (~ 90s including TTS)
python build.py --no-audio  # fast iteration (skip TTS)
python build.py --no-package # asset-only refresh
python app.py               # run from source without packaging
```

## Documents

- [BREAKDOWN.md](BREAKDOWN.md) — what's built and why (technical)
- [TUTORIAL.md](TUTORIAL.md) — how a parent or kid uses it
- [HANDOFF.md](HANDOFF.md) — co-worker / AI handoff notes

License: MIT (project), CC0 (procedurally-generated mascot art).

## TL;DR

---

## Publisher

Published by **Revolutionary Designs**.  
GitHub: https://github.com/awesomo913  
Contact: solidgoldbarsinmycloset@gmail.com  <!-- pii-ok: official brand contact -->

