---
public-visible: true
last-reviewed: 2026-05-07
reviewer: the designer
---

# Kids Code Academy — Plain-Language Proof

## What this thing is
A small program that teaches a 7-year-old how to use computer helpers (the kind that talk back) safely, on their own, with no internet risk.

## What it does for you
- Plays short voiced lessons by a friendly robot mascot named Bytey.
- Lets the child practice with mini-games — tapping, typing, dragging, sequencing — that gate each multiple-choice question, so the child has to actually engage before guessing.
- Shows a fresh wording of every question on every visit, so the child cannot speed-click from memory.
- Tracks progress quietly in a private folder on the family's own machine. Nothing leaves the computer.
- Lets a parent open a hidden dashboard (PIN required) to see what the child has done.

## How it was made
The user designed this. He set the goal — teach his son the way he himself works with computer helpers — and chose the rules: no internet, no real outside helpers, easy enough for a 7-year-old to use alone. AI helped translate the design into running code, art, and voice files. The user reviewed each major decision before code was written.

## What it costs / what it gives back
- **Money:** $0. The whole thing is one file the family double-clicks. There is no subscription, no purchase inside the app, no ads.
- **Time:** Lessons are short — about 3 to 6 minutes each. There are 60 lessons total.
- **Data:** Nothing leaves the family's computer. No accounts. No server. No tracking. The child's progress lives only on the family's own machine.
- **Control:** The parent owns the file. They can delete it any time and it is fully gone. No outside service has any record.
- **Trade-off:** The "helpers" the child meets in the lessons are pretend versions, not the real thing. That's intentional — the child practices the skill of asking for help without ever connecting to a live system that could charge money or behave unexpectedly. The child learns the habit; the real helpers come later.

## Who is responsible
The designer (the user) is the sole owner and decision-maker. Last review: 2026-05-07.

## What proof exists that it works
- The program runs as a single file on Windows (one double-click, no install).
- A Raspberry Pi version has been built and ships from the same source code.
- A 50-cycle automated test confirms that the child's progress is saved correctly across closing and re-opening the app.
- All 60 lessons load. 1,500 question variations across the 60 lessons protect against the child memorizing answers — every visit shows a different wording in a different order.
- The mini-game gate prevents speed-guessing — the child must complete the demonstrated interaction before the answer choices appear.
- Build artifacts and run logs live alongside the source for any future review.

## Changelog
- **2026-05-07** — Added a way to stop the child from memorizing answers. Every question now appears in five different wordings, picked at random each time. Added 4 to 7 questions per lesson instead of just one. The answer choices stay hidden until the child completes the small demonstration that goes with the question, so they can no longer click through without paying attention.
- **2026-05-07** — Built a version that runs on Raspberry Pi computers using the same source code as the Windows version.
- **2026-05-05** — Added an "Idea Lab" set of lessons where the child practices coming up with their own ideas and turning them into small projects.
- **2026-05-04** — Fixed the bug where the child's progress would sometimes reset when the program was reopened. Progress now stays put even after the computer restarts.
- **2026-05-03** — Doubled the number of lessons from a small starter set to a full 55-lesson curriculum, then added a parent dashboard to see what the child has done.
- **2026-05-01** — First version shipped. Bytey the robot, voiced lessons, and the first set of mini-games.
