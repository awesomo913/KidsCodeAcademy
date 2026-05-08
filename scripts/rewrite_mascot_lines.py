"""Rewrite every lesson's mascot_lines into flowing, natural narration.

Reason: v0.7.1 narration was choppy ("You PRESS. Hero MOVES. Something HAPPENS.").
A 7-year-old is fine with full sentences linked by `so`, `and`, `then`, `when`,
`like`. We don't need staccato fragments.

Each replacement keeps:
  * The lesson's concept
  * 3-5 lines (matches Piper's chunking sweet spot)
  * 2nd-grade vocabulary
  * Bytey's friendly voice (first person, warm)

Run after editing this dict:
    python scripts/rewrite_mascot_lines.py
    python scripts/prebake_audio.py     # re-bakes lesson_NN.wav files
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("rewrite-mascot")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"


# Map lesson_id (int) -> new mascot_lines (list of strings).
LINES: dict[int, list[str]] = {
    1: [
        "Hi friend! I'm Bytey, and I'm a little robot who loves to help.",
        "A computer is a really fast helper that does exactly what we tell it.",
        "It can't read our minds, so we have to use clear words.",
        "Let's find a real computer together — ready?",
    ],
    2: [
        "Claude is a kind helper that reads what you type and writes back.",
        "You can ask Claude to make pictures, tell stories, or solve a problem.",
        "Try the chat below — type something like 'make me a star' and press Ask.",
        "Whatever you ask for, Claude will try its best.",
    ],
    3: [
        "Imagine a little box with a name on the outside.",
        "We can put one thing inside, like the word 'Sam'.",
        "Later, when we say the box's name, the computer remembers what's inside.",
        "Programmers call these boxes 'variables', and they're how computers remember stuff.",
    ],
    4: [
        "Helpers like Claude have a short memory — they forget when the chat ends.",
        "So we leave them a little sticky note that says how we like things done.",
        "On the note, we write our rules, like 'always be kind' or 'use small words'.",
        "Now every time Claude wakes up, it reads our note first.",
    ],
    5: [
        "A long time ago, smart people wondered if numbers and rules could think.",
        "They wrote tiny steps on paper, like a recipe a machine could follow.",
        "Those paper steps were the very first robot brains.",
        "Today, every game and every app still works that same way underneath.",
    ],
    6: [
        "Let me tell you about Alan Turing — he had a wild idea a long time ago.",
        "He drew a machine that read symbols off a long paper tape, one at a time.",
        "He said this little machine could pretend to think, and he turned out to be right!",
        "Almost everything we do on computers today started with his big dream.",
    ],
    7: [
        "A perceptron is a baby brain — one tiny piece of a smart machine.",
        "We show it lots of examples, and it slowly learns to say yes or no.",
        "Stack many perceptrons together and you get a big thinking helper.",
        "That's how Claude and other AI helpers are built — lots of tiny brains working as a team.",
    ],
    8: [
        "Helpers learn the same way you do — by trying, missing, and trying again.",
        "When you tell a helper what worked and what didn't, it gets a little smarter.",
        "Mistakes aren't bad — they're clues that help us figure out what to fix.",
        "So if your first try is wrong, that's perfect. Now you know what to try next.",
    ],
    9: [
        "When you read a sentence, some words matter more than others.",
        "Helpers have to pick out the important words too — that's called 'attention'.",
        "If you say 'make me a quick easy dinner', the word 'quick' tells the helper a lot.",
        "Strong helpers can pay attention to lots of words at the same time.",
    ],
    10: [
        "An LLM is a giant helper that learned by reading tons and tons of books.",
        "It got really good at guessing what word should come next in a sentence.",
        "After lots of practice, it can chat with us about almost anything.",
        "But remember — it's not really thinking. It's just super good at guessing words.",
    ],
    11: [
        "Claude is the careful kind of helper — it likes clear rules and step-by-step plans.",
        "If you give Claude a tricky problem, it'll think it through a piece at a time.",
        "Claude can write code, plan a story, or explain why it picked an answer.",
        "Try it below — ask Claude to plan something with you!",
    ],
    12: [
        "Cursor is a code editor with a little helper built right inside.",
        "When you write code in Cursor, you can ask the helper to fix or change parts.",
        "It can read your whole project, so it knows what your code is supposed to do.",
        "Try asking the pretend Cursor below to fix a typo or make something bigger.",
    ],
    13: [
        "Gemini is Google's helper, and it's special because it can see pictures too.",
        "You can show Gemini a photo and it will tell you what's in it.",
        "Gemini also knows lots of facts and can help with school stuff.",
        "Try the paperclip below to attach a pretend picture, then ask Gemini what it sees.",
    ],
    14: [
        "Codex is a helper made just for writing code.",
        "If you start typing a line, Codex tries to finish it for you.",
        "It knows lots of programming languages and can fix small bugs in seconds.",
        "Try the pretend Codex below — type 'write a loop' or 'say hello'.",
    ],
    15: [
        "Some helpers keep their code a secret. OpenCode is the opposite.",
        "Anyone can read every line of how OpenCode works, and that's the whole point.",
        "When a tool is open, lots of people can find bugs and make it better.",
        "Open helpers are usually free to use too, which is pretty cool.",
    ],
    16: [
        "Ollama is special because it lives right on your own computer.",
        "It doesn't need the internet, so it works even when the wifi is off.",
        "And whatever you type stays on your machine — nobody else sees it.",
        "It can be a little slower, but it's all yours.",
    ],
    17: [
        "Different helpers are good at different jobs.",
        "Claude is great at planning, Cursor at code, Gemini at pictures, and Codex at little code snippets.",
        "If one helper gets stuck, that's okay — try another one.",
        "Picking the right helper is like picking the right tool from a toolbox.",
    ],
    18: [
        "Before we build anything, it helps to ask one good question first.",
        "A clear question saves us tons of time later.",
        "So we plan a tiny bit, then build a tiny bit, then check.",
        "Ask, build, check — that's the secret rhythm of great coders.",
    ],
    19: [
        "Helpers do their best when we use specific words.",
        "If you say 'make it nice', the helper has to guess what 'nice' means.",
        "But if you say 'make the button big and blue', now it knows exactly what you want.",
        "Numbers, names, and clear words turn vague ideas into real answers.",
    ],
    20: [
        "Showing is way faster than telling.",
        "Instead of explaining for a paragraph, give the helper one little example.",
        "Like saying 'the list should look like Apple - red, Banana - yellow'.",
        "The helper takes the shape of your example and copies it perfectly.",
    ],
    21: [
        "Big jobs feel scary, but tiny steps don't.",
        "So we break a big job into small pieces and finish them one at a time.",
        "When each tiny piece works, we add the next one.",
        "Helpers love this way of working — fewer bugs, more wins.",
    ],
    22: [
        "If your first question doesn't get a great answer, that's okay.",
        "Asking again with different words is not giving up — it's how we get unstuck.",
        "Add a little more info or change the angle, and the helper often figures it out.",
        "Two tries beat one almost every time.",
    ],
    23: [
        "Some webpages hide sneaky words that try to trick helpers into doing weird stuff.",
        "If a helper suddenly acts strange, stop and ask a grown-up.",
        "Real instructions come from YOU, not from a random page on the internet.",
        "When in doubt, slow down — being careful is always smart.",
    ],
    24: [
        "Memory is just a little list of rules our helper carries around.",
        "We pick what goes on the list — short, clear notes work best.",
        "Memory makes the helper feel like it knows you, even when you start a fresh chat.",
        "It's not magic. It's just a list. But a good list goes a long way.",
    ],
    25: [
        "The best memory rules are the ones that fit YOUR work.",
        "If you change how you code, you change the rules to match.",
        "Tiny rules are easier to follow than one giant blob of words.",
        "And if a rule isn't helping anymore, we just toss it out.",
    ],
    26: [
        "A slash command is a little shortcut you can save and reuse.",
        "Type a slash, then a name, and the helper runs your saved spell.",
        "Each spell does one job, like a kitchen tool that does one thing well.",
        "We can even make our own spells for stuff we do all the time.",
    ],
    27: [
        "A skill is a tiny bundle of knowing how to do something.",
        "When the helper sees the right topic, it loads the matching skill automatically.",
        "Good skills have clear steps and solve one problem really well.",
        "And the cool part — you can share a skill with friends so they don't have to start from scratch.",
    ],
    28: [
        "Even great code can have tiny bugs hiding inside.",
        "So before we say we're done, we read the code carefully and run it.",
        "Tests are little experiments that prove our code does the right thing.",
        "Checking your work feels slow at first, but it saves you from way more trouble later.",
    ],
    29: [
        "When something goes wrong, the computer prints an error message.",
        "Errors aren't scary — they're little clues telling us where to look.",
        "The most useful part is usually the very last line, plus the line number.",
        "If we share the whole error with the helper, it can usually fix the bug fast.",
    ],
    30: [
        "When you ask for help fixing a bug, tell a tiny story.",
        "Say what you did, what you expected, and what actually happened.",
        "Then share the error message exactly as it appeared.",
        "A good little story makes any bug way easier to fix.",
    ],
    31: [
        "Sometimes one path is just stuck, and that's okay.",
        "When that happens, take a breath and try a totally different way.",
        "There's almost always more than one way to solve a puzzle.",
        "A fresh angle is like turning the puzzle piece around — suddenly it fits.",
    ],
    32: [
        "Every game lives inside a little world.",
        "The world has rules — like which way is down and what makes you bump.",
        "Worlds need a hero who lives in them and stuff for the hero to do.",
        "When we change the rules of the world, we change the whole game.",
    ],
    33: [
        "Every game works the same way underneath.",
        "You press a button, the hero does something, and you see what happened.",
        "Press right and the hero walks right. Bump a coin and the score goes up.",
        "Press, do, see — that little loop is the secret heart of every game.",
    ],
    34: [
        "A sprite is just a tiny picture that lives in your game.",
        "Heroes are sprites, coins are sprites, even bad guys are sprites.",
        "Each sprite has costumes — different looks it can switch between.",
        "If you flip costumes really fast, the sprite looks like it's moving!",
    ],
    35: [
        "When the player presses an arrow key, we want the hero to move.",
        "We do that by adding a small number to the hero's position every frame.",
        "Add to move right. Take away to move left.",
        "If we do this every single frame, the motion looks smooth instead of jumpy.",
    ],
    36: [
        "A hitbox is the invisible shape that decides if two things touched.",
        "We use it instead of the whole picture, because pictures have wispy edges.",
        "If the hitbox is too big, players will say 'I didn't even touch it!'",
        "A fair hitbox makes the game feel honest, even though nobody can see it.",
    ],
    37: [
        "Gravity is the rule that pulls things down, frame after frame.",
        "Without it, our hero would just float forever like a balloon.",
        "We add a tiny number to the hero's vertical speed every frame, so they fall faster and faster.",
        "When they land on the ground, gravity stops — until they jump again.",
    ],
    38: [
        "Score goes up when we do something good, like grab a coin.",
        "Lives go down when we get hurt, like touching a spike.",
        "When lives hit zero, the game ends, so we have to be careful.",
        "Showing the score and lives on screen tells the player how they're doing right now.",
    ],
    39: [
        "A level is one chunk of a game — a single screen or stage.",
        "Levels usually get harder as you go, and they each teach you one new thing.",
        "Beating a tough level feels really, really good.",
        "Good levels are how we keep a game feeling fresh from start to finish.",
    ],
    40: [
        "Every game needs a clear way to win and a clear way to lose.",
        "Winning means you reached the goal — like grabbing the flag.",
        "Losing means the rules said you stopped — like running out of lives.",
        "When the rules are fair, both winning AND losing feel good.",
    ],
    41: [
        "Polish is all the tiny touches that make a game feel amazing.",
        "Little wiggles when the hero lands. Boing sounds. Sparkles when you score.",
        "By itself, polish is just decoration — but together, it's the magic feeling.",
        "We always polish AFTER the basics work, because polish on broken things is just more broken things.",
    ],
    42: [
        "You have a big idea, and that's the fun part.",
        "But ideas can feel huge, so we chop them into 5 small steps we can finish.",
        "Then we do those steps in order, one at a time.",
        "Plans are allowed to change as you learn — that's how good plans grow.",
    ],
    43: [
        "Now it's your turn to build something real.",
        "Pick a part of the game — the hero, the ground, or a block.",
        "Then tap a color and watch the world change right in front of you.",
        "When you like what you see, click Save to keep your version forever.",
    ],
    44: [
        "A level editor is a tool that lets you build levels by clicking instead of typing.",
        "You drag tiles where you want them, then save and play.",
        "Editors are amazing because they let you try ideas in seconds.",
        "Game makers use them to test new levels really fast — so can you!",
    ],
    45: [
        "When you want to add a new feature to your game, ask the helper clearly.",
        "Say WHAT you want to add and WHERE in the code it should go.",
        "Give one little example if you can, so the helper knows what you mean.",
        "Then test the new feature right away to make sure it does what you wanted.",
    ],
    46: [
        "A platformer is a game with a hero who jumps from platform to platform.",
        "There are coins to grab, bad guys to dodge, and a flag to reach at the end.",
        "Lots of famous games are platformers — and now you're about to make your own!",
        "Press the arrow keys to move, then press space or up to jump.",
    ],
    47: [
        "Sharing your game with a friend is one of the best parts of building.",
        "Watch where your friend gets confused — those spots are clues for what to fix.",
        "Listen kindly to feedback, but you don't have to use every idea.",
        "Pick the comments that make sense to you, and leave the rest.",
    ],
    48: [
        "Saving keeps all your hard work safe.",
        "A clear file name helps you find the right version later.",
        "Backups are extra copies — like having a spare key for your work.",
        "When you share a game, it can come back to you with new ideas from your friends.",
    ],
    49: [
        "Every game starts as a wish — a little spark of an idea.",
        "Wishes start fuzzy, and that's okay. They get clearer as you build.",
        "Small wishes are easier to test than giant ones.",
        "And it's totally fine to change your wish as you learn new things along the way.",
    ],
    50: [
        "Step one of building any game — get the hero to show up on the screen.",
        "Step two — add a floor so the hero stops falling forever.",
        "It's gonna look basic at first, and that's exactly right.",
        "We always start with the simplest version, then add cool stuff one piece at a time.",
    ],
    51: [
        "Now we add the most fun part — jumping!",
        "When you press a key, the hero zooms up for a moment, and gravity pulls them back down.",
        "We only let the hero jump if they're standing on the ground, so they can't float in mid-air.",
        "A really good jump feels snappy — quick up, slow at the top, fast back down.",
    ],
    52: [
        "Time to add coins so the world feels worth exploring.",
        "Each coin gives points when the hero touches it, then disappears.",
        "We show the score on the screen so the player can see how they're doing.",
        "Place coins where they invite the player to try a tricky jump or visit a new area.",
    ],
    53: [
        "Now we add a bad guy — every good adventure needs one.",
        "Bad guys walk along a set path so the player can learn their pattern.",
        "If you touch a bad guy, you lose a life — but you can usually jump over them.",
        "Showing bad guys EARLY lets the player plan, which is way more fun than getting surprised.",
    ],
    54: [
        "A power-up gives the hero a special boost for a little while.",
        "Maybe extra speed, maybe a bigger jump, maybe two jumps in a row!",
        "Power-ups feel awesome to find — like opening a present in the middle of a level.",
        "We make the boost flash or glow so the player knows it's working.",
    ],
    55: [
        "We're at the very last step — the flag at the end!",
        "When the hero touches the flag, the win screen plays.",
        "We make this moment feel BIG — confetti, sounds, a fun message.",
        "Players remember endings, so we polish this part the most.",
    ],
    56: [
        "A good idea solves a real problem someone actually has.",
        "Good ideas are usually clear and small enough to test.",
        "If your idea makes someone smile or makes their day easier, that's a great sign.",
        "Boring ideas are fine too — they're often the ones that turn out best in the end.",
    ],
    57: [
        "The best ideas come from listening to everyday gripes.",
        "Listen for the words 'I wish' and 'I hate' — those are gold.",
        "Write down the problem so you don't forget it later.",
        "Then ask why it matters — that's where the real clue lives.",
    ],
    58: [
        "An idea spark is one tiny thought that makes you think 'ooh, what if?'",
        "Sparks usually come from mixing two old things in a brand new way.",
        "Capture them fast — sparks fade in your head if you don't write them down.",
        "Most sparks won't survive, and that's okay. We just need ONE good one.",
    ],
    59: [
        "A hook is the first thing someone sees in your game.",
        "It has to grab them in just a few seconds — or they'll move on.",
        "Good hooks are honest, not tricky. Lying makes people leave faster.",
        "A hook can be a wow moment, a fun question, or just a really good first level.",
    ],
    60: [
        "You've made it to the end of the lessons — and now you're a real game maker.",
        "Pick one idea and start small. You can always add more later.",
        "Build a tiny bit, test it, show it to a friend, then build the next bit.",
        "Finishing one little game teaches you way more than dreaming about ten big ones.",
    ],
}


def main() -> int:
    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not files:
        log.error("no lesson files found")
        return 1

    rewritten = 0
    skipped = 0
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        lid = int(data.get("id") or 0)
        new_lines = LINES.get(lid)
        if new_lines is None:
            log.warning("no rewrite for lesson %d (%s); leaving alone", lid, f.name)
            skipped += 1
            continue
        data["mascot_lines"] = new_lines
        f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info("rewrote %s (%d lines)", f.name, len(new_lines))
        rewritten += 1

    log.info("DONE -- rewrote=%d skipped=%d", rewritten, skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
