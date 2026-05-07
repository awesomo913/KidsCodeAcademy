# Kids Code Academy

A safe, offline coding tutorial for ages 7+. Teaches the same workflow grown-ups use with Claude, Cursor, and Gemini — but with a cartoon robot mascot, read-aloud audio, and mini-games instead of walls of text.

## Install (Windows)

**Option 1 — One-line PowerShell installer (downloads + verifies + launches):**

```powershell
irm https://raw.githubusercontent.com/awesomo913/KidsCodeAcademy/main/install.ps1 | iex
```

The installer drops `KidsCodeAcademy.exe` on your Desktop, verifies the SHA-256 against the pinned hash, and launches it. No admin rights, no registry edits.

**Option 2 — Manual download:**

1. Grab the EXE from the [Releases page](https://github.com/awesomo913/KidsCodeAcademy/releases/latest).
2. Double-click `KidsCodeAcademy.exe`. That's it.

Verify by hash (optional): `Get-FileHash KidsCodeAcademy.exe -Algorithm SHA256` should match the value pinned in [install.ps1](install.ps1).

## Install (Raspberry Pi — Pi OS bookworm or later)

**One-line installer + builder.** Paste this into your Pi's terminal (or a Pi Connect remote shell):

```bash
curl -fsSL https://raw.githubusercontent.com/awesomo913/KidsCodeAcademy/main/scripts/build_pi.sh | bash
```

What it does:
1. Installs `python3 + python3-gi + gir1.2-webkit2-4.1` via `apt`
2. Clones the repo to `~/KidsCodeAcademy`
3. Sets up a Python venv with `pywebview + pillow + pyinstaller` (no TTS — audio is pre-baked and committed to the repo)
4. Runs `python build.py --target=pi` to produce a single ARM64 binary
5. Drops it on your Desktop as `KidsCodeAcademy` (chmod +x) and creates a `.desktop` launcher entry

Double-click the binary on the Desktop. First launch ~6 s while WebKitGTK warms up; subsequent launches are faster.

**Tested on:** Raspberry Pi 4 / 5 with 64-bit Pi OS bookworm. Pi Zero 2 W works but boot is slower (~10 s).

**Manual run from source** (no packaging — useful for dev):
```bash
cd ~/KidsCodeAcademy
source .venv/bin/activate
python3 app.py
```

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

