"""Author all v0.3.0 net-new lesson JSONs in one shot.

This script writes lessons 5-17, 19-22, 24-27, 29-42, 44-46, 49-55 (45 lessons)
matching the canonical schema in lesson_02_talking_to_claude.json + the v0.3
hints block. Each lesson:
  - id           : new lesson number (1-55)
  - title        : kid-language title
  - goal         : 2nd-grade reading level
  - sticker_emoji: a celebratory emoji
  - mascot_lines : 2-5 short lines for narration
  - hints        : tier1 highlight + tier2 rephrase + tier3 nudge
  - game         : { type, payload } for one of the 6 existing or 3 new mini-game types
  - sandbox      : optional { helpers, hint } for chat-driven lessons
  - chapter      : "ch1".."ch9" for sidebar grouping

Run: python scripts/author_lessons.py
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("author")

ROOT = Path(__file__).resolve().parent.parent
LESSONS = ROOT / "lessons"


def write(filename: str, data: dict) -> None:
    LESSONS.mkdir(parents=True, exist_ok=True)
    p = LESSONS / filename
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log.info("wrote %s", filename)


# === Chapter 2 — How AI Got Here ============================================
# Animated history scenes. game type = "history-scene".

write("lesson_05_math_made_thinking.json", {
    "id": 5, "chapter": "ch2",
    "title": "Math Made Thinking",
    "goal": "Numbers and rules can act like a tiny brain.",
    "sticker_emoji": "🧮",
    "mascot_lines": [
        "Long ago, smart people had a big idea.",
        "What if numbers and rules could think?",
        "They wrote little steps on paper.",
        "That paper was the FIRST robot brain.",
    ],
    "hints": {
        "tier1": {"highlight": "math steps"},
        "tier2": {"rephrase": "Watch the scene. Then put the math steps in the right order."},
        "tier3": {"nudge": "First we ADD, then we CHECK if it is more than five."},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Order these math steps to act like a tiny brain:",
            "steps": ["Start at 0", "Add 1", "Check if more than 5", "If yes, stop"],
        },
    },
})

write("lesson_06_turing_dream.json", {
    "id": 6, "chapter": "ch2",
    "title": "Turing's Big Dream",
    "goal": "A man drew a machine that could pretend to be smart.",
    "sticker_emoji": "📜",
    "mascot_lines": [
        "Meet Alan Turing. He had a wild idea.",
        "He drew a machine on paper.",
        "It read symbols on a long tape.",
        "He said: this could pretend to think.",
        "He was right. We still use his ideas today!",
    ],
    "hints": {
        "tier1": {"highlight": "tape"},
        "tier2": {"rephrase": "Pick the part of Turing's machine that holds the symbols."},
        "tier3": {"nudge": "It is a long, skinny thing. Like a roll of paper."},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which part of Turing's pretend machine holds the symbols?",
            "choices": [
                {"label": "📼 Tape", "right": True},
                {"label": "🪑 Chair", "right": False},
                {"label": "🍎 Apple", "right": False},
                {"label": "🎈 Balloon", "right": False},
            ],
        },
    },
})

write("lesson_07_perceptron_pet.json", {
    "id": 7, "chapter": "ch2",
    "title": "The First Robot Brain Cell",
    "goal": "One pretend brain cell says yes or no.",
    "sticker_emoji": "🧠",
    "mascot_lines": [
        "Inside your head, you have brain cells.",
        "Robots have pretend ones too.",
        "One pretend brain cell looks at numbers.",
        "Then it says YES or NO. That is all!",
        "Many of them stacked together can do BIG things.",
    ],
    "hints": {
        "tier1": {"highlight": "yes or no"},
        "tier2": {"rephrase": "A perceptron only knows two answers. Match each input to its answer."},
        "tier3": {"nudge": "Hot food = yes for cool, no for eat. Use your nose!"},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "A robot brain cell says YES or NO. Drag each thing to its answer:",
            "pairs": [
                {"left": "🌧️ It is raining", "right": "YES bring umbrella"},
                {"left": "☀️ Big sunny day", "right": "NO umbrella needed"},
                {"left": "🥵 Hot pizza", "right": "YES wait to cool"},
                {"left": "🥶 Cold ice cream", "right": "NO eat it now"},
            ],
        },
    },
})

write("lesson_08_back_and_forth_learning.json", {
    "id": 8, "chapter": "ch2",
    "title": "Back-and-Forth Learning",
    "goal": "Robots get smart by guessing, missing, and trying again.",
    "sticker_emoji": "🔁",
    "mascot_lines": [
        "How do robots get smart? They GUESS.",
        "They guess, they miss, and they fix.",
        "Then they guess again. A little better.",
        "Do that a million times. Boom! Smart robot!",
    ],
    "hints": {
        "tier1": {"highlight": "order"},
        "tier2": {"rephrase": "Put the steps a robot uses to get smart in order."},
        "tier3": {"nudge": "Always guess BEFORE you check, and check BEFORE you fix."},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Order the back-and-forth learning loop:",
            "steps": ["Guess the answer", "Check if it is right", "Fix what was wrong", "Try again"],
        },
    },
})

write("lesson_09_word_attention.json", {
    "id": 9, "chapter": "ch2",
    "title": "Words That Look at Each Other",
    "goal": "A new trick let robots read whole sentences at once.",
    "sticker_emoji": "👀",
    "mascot_lines": [
        "Old robots read words ONE at a time.",
        "Then a new trick came along.",
        "Now words can LOOK at each other.",
        "The word 'it' looks back to find what 'it' means.",
        "This made robots SO much smarter!",
    ],
    "hints": {
        "tier1": {"highlight": "looks at"},
        "tier2": {"rephrase": "Match each word to the word it looks at to know what it means."},
        "tier3": {"nudge": "She/he look back to find a name. It looks at things."},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "Each little word looks at another word. Match them up!",
            "pairs": [
                {"left": "Sam is happy. He smiles.", "right": "He → Sam"},
                {"left": "Mom hugged Lily. She is small.", "right": "She → Lily"},
                {"left": "I bought a cat. It purrs.", "right": "It → cat"},
            ],
        },
    },
})

write("lesson_10_llm_is_born.json", {
    "id": 10, "chapter": "ch2",
    "title": "And Then Came Big Language Models",
    "goal": "Big language models are word-guessers grown HUGE.",
    "sticker_emoji": "🌟",
    "mascot_lines": [
        "Take all those tricks. Mix them up.",
        "Make the robot's brain HUGE.",
        "Show it a billion books.",
        "And what do you get? Claude! Gemini! Cursor!",
        "All they really do is GUESS the next word. Really, really well!",
    ],
    "hints": {
        "tier1": {"highlight": "next word"},
        "tier2": {"rephrase": "An LLM is just a robot that guesses what word comes next."},
        "tier3": {"nudge": "Stack the four word-blocks: It / guesses / the / next-word."},
    },
    "game": {
        "type": "place-blocks",
        "payload": {
            "prompt": "Build the sentence in order:",
            "blocks": ["It", "guesses", "the", "next word"],
            "solution": ["It", "guesses", "the", "next word"],
        },
    },
})

# === Chapter 3 — Meet Every Helper ==========================================

write("lesson_11_claude_in_depth.json", {
    "id": 11, "chapter": "ch3",
    "title": "Claude, the Big-Picture Helper",
    "goal": "Claude reads lots and plans careful steps.",
    "sticker_emoji": "📚",
    "mascot_lines": [
        "Meet Claude. Claude reads BIG things.",
        "Claude makes plans. Step one, step two, step three.",
        "Ask Claude to plan a story.",
        "Claude will think first, THEN write.",
    ],
    "hints": {
        "tier1": {"highlight": "plan"},
        "tier2": {"rephrase": "Claude is the planner. Ask Claude for a 3-step plan."},
        "tier3": {"nudge": "Use the words 'plan a story' or 'three steps' in your prompt."},
    },
    "sandbox": {"helpers": ["claude"], "hint": "Try: 'plan a 3-step bedtime story'."},
    "game": {
        "type": "guided-talk",
        "payload": {
            "prompt": "Read about Claude out loud:",
            "lines": [
                "Claude is the big-picture helper.",
                "Claude reads lots of pages at once.",
                "Claude likes to PLAN before doing.",
                "Ask Claude to make a plan!",
            ],
        },
    },
})

write("lesson_12_cursor_in_depth.json", {
    "id": 12, "chapter": "ch3",
    "title": "Cursor, the Fast-Edit Helper",
    "goal": "Cursor sits in your code and changes one tiny part.",
    "sticker_emoji": "✏️",
    "mascot_lines": [
        "Meet Cursor. Cursor is fast.",
        "Cursor lives inside your code.",
        "Need to fix one line? Ask Cursor.",
        "Done. Saved. On to the next thing!",
    ],
    "hints": {
        "tier1": {"highlight": "one line"},
        "tier2": {"rephrase": "Cursor changes small parts fast. Pick the line that needs fixing."},
        "tier3": {"nudge": "The line with a typo or a wrong word is the one to fix!"},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Cursor needs to fix one tiny thing. Which line has a typo?",
            "choices": [
                {"label": "Hello, world!", "right": False},
                {"label": "Hellpp, world!", "right": True},
                {"label": "Goodbye!", "right": False},
                {"label": "Have a nice day!", "right": False},
            ],
        },
    },
})

write("lesson_13_gemini_in_depth.json", {
    "id": 13, "chapter": "ch3",
    "title": "Gemini, the Big-Library Helper",
    "goal": "Gemini knows facts and can look at pictures.",
    "sticker_emoji": "🌐",
    "mascot_lines": [
        "Meet Gemini. Gemini knows LOTS.",
        "Gemini learned from a giant library.",
        "Show Gemini a picture. It can tell you what it is!",
        "Ask Gemini a fact. It will share what it knows.",
    ],
    "hints": {
        "tier1": {"highlight": "facts"},
        "tier2": {"rephrase": "Gemini is great for facts. Match each helper to its job."},
        "tier3": {"nudge": "Big plan = Claude. Quick edit = Cursor. Fact = Gemini."},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "Match each helper to its best job:",
            "pairs": [
                {"left": "Plan a treehouse", "right": "Claude"},
                {"left": "Fix a typo fast", "right": "Cursor"},
                {"left": "How big is the moon?", "right": "Gemini"},
            ],
        },
    },
})

write("lesson_14_codex_in_depth.json", {
    "id": 14, "chapter": "ch3",
    "title": "Codex, the Tiny Coder",
    "goal": "Codex is a small helper that writes short code in your terminal.",
    "sticker_emoji": "💻",
    "mascot_lines": [
        "Meet Codex. Codex is small but mighty.",
        "Codex lives in a black box called a TERMINAL.",
        "Type a wish. Codex types code!",
        "Great for small jobs that you do over and over.",
    ],
    "hints": {
        "tier1": {"highlight": "terminal"},
        "tier2": {"rephrase": "Codex works step by step in a terminal. Order the steps."},
        "tier3": {"nudge": "First read the wish. Then write code. Then save. Then run!"},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Order Codex's steps:",
            "steps": ["Read your wish", "Write the code", "Save the file", "Run the code"],
        },
    },
})

write("lesson_15_opencode_in_depth.json", {
    "id": 15, "chapter": "ch3",
    "title": "OpenCode, the Free Helper",
    "goal": "OpenCode is open — anyone can see how it works.",
    "sticker_emoji": "🔓",
    "mascot_lines": [
        "Some helpers are CLOSED.",
        "You can use them, but not peek inside.",
        "OpenCode is OPEN.",
        "Anyone can see how it works. Anyone can fix it!",
        "Open is great for learning.",
    ],
    "hints": {
        "tier1": {"highlight": "see inside"},
        "tier2": {"rephrase": "Open helpers let you peek inside. Closed ones don't."},
        "tier3": {"nudge": "OpenCode is OPEN. ChatGPT is CLOSED. Drag each one home!"},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "Open or closed? Drag each helper to the right side:",
            "pairs": [
                {"left": "OpenCode", "right": "🔓 OPEN"},
                {"left": "Ollama", "right": "🔓 OPEN"},
                {"left": "ChatGPT", "right": "🔒 CLOSED"},
            ],
        },
    },
})

write("lesson_16_ollama_local.json", {
    "id": 16, "chapter": "ch3",
    "title": "Ollama: A Robot On YOUR Computer",
    "goal": "A LOCAL robot lives in your computer. No WiFi. Just slower.",
    "sticker_emoji": "🏠",
    "mascot_lines": [
        "Most robots live online. They need WiFi.",
        "Ollama is different. Ollama lives RIGHT HERE.",
        "Right inside your computer.",
        "No WiFi? Ollama still works.",
        "It is a little slower. But it is YOURS!",
    ],
    "hints": {
        "tier1": {"highlight": "computer"},
        "tier2": {"rephrase": "Ollama lives WHERE? On your computer or online?"},
        "tier3": {"nudge": "Local means HOME. Ollama's home is your computer!"},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Type 'hi' and see what your local helper says!",
    },
    "game": {
        "type": "place-blocks",
        "payload": {
            "prompt": "Build the sentence:",
            "blocks": ["Ollama", "lives", "on my", "computer"],
            "solution": ["Ollama", "lives", "on my", "computer"],
        },
    },
})

write("lesson_17_pick_the_helper.json", {
    "id": 17, "chapter": "ch3",
    "title": "Pick the Right Helper",
    "goal": "Different jobs need different friends.",
    "sticker_emoji": "🤝",
    "mascot_lines": [
        "You have lots of helpers now!",
        "Claude. Cursor. Gemini. Codex. OpenCode. Ollama.",
        "Each is best at a different job.",
        "Pick the right friend for the job!",
    ],
    "hints": {
        "tier1": {"highlight": "right friend"},
        "tier2": {"rephrase": "Big plan? Claude. Quick edit? Cursor. Fact? Gemini. Local? Ollama."},
        "tier3": {"nudge": "Plan a long story = Claude. Fact about cats = Gemini. Fix one line = Cursor!"},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "Match each job to the best helper:",
            "pairs": [
                {"left": "Plan a long story", "right": "Claude"},
                {"left": "Fix one tiny line", "right": "Cursor"},
                {"left": "Tell me about pandas", "right": "Gemini"},
                {"left": "Help me without WiFi", "right": "Ollama"},
            ],
        },
    },
})

# === Chapter 4 — Talking Smart (4 net new — existing 18, 23 already shipped) ==

write("lesson_19_be_specific.json", {
    "id": 19, "chapter": "ch4",
    "title": "Be Super Specific",
    "goal": "A fuzzy ask gets a fuzzy answer. Add details!",
    "sticker_emoji": "🎯",
    "mascot_lines": [
        "Watch this. I say 'a dog'. The robot draws... ANY dog.",
        "Now I say 'a small red dog with one floppy ear'.",
        "WAY better dog!",
        "Details give the robot a target.",
    ],
    "hints": {
        "tier1": {"highlight": "details"},
        "tier2": {"rephrase": "Pick the message that has the most clear details."},
        "tier3": {"nudge": "Look for size, color, and special parts. More words = clearer picture."},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which prompt is the MOST specific?",
            "choices": [
                {"label": "Make a thing.", "right": False},
                {"label": "Make a small red dog with one floppy ear.", "right": True},
                {"label": "A dog!", "right": False},
                {"label": "Idk.", "right": False},
            ],
        },
    },
})

write("lesson_20_show_dont_tell.json", {
    "id": 20, "chapter": "ch4",
    "title": "Show, Don't Just Tell",
    "goal": "Add an example so the robot copies the shape.",
    "sticker_emoji": "🪞",
    "mascot_lines": [
        "Sometimes telling is not enough.",
        "Show the robot a small example.",
        "Then it copies the SHAPE of what you want.",
        "Like a kid following a recipe!",
    ],
    "hints": {
        "tier1": {"highlight": "example"},
        "tier2": {"rephrase": "Pick the message that gives the robot a tiny example to copy."},
        "tier3": {"nudge": "Examples often start with 'like this:' and show a sample."},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which prompt SHOWS instead of just tells?",
            "choices": [
                {"label": "Make a name.", "right": False},
                {"label": "Make a name like this: Bytey, Sparky, Whiskers.", "right": True},
                {"label": "Names please.", "right": False},
                {"label": "Just one name.", "right": False},
            ],
        },
    },
})

write("lesson_21_one_at_a_time.json", {
    "id": 21, "chapter": "ch4",
    "title": "One Step at a Time",
    "goal": "Big jobs split into little steps.",
    "sticker_emoji": "🪜",
    "mascot_lines": [
        "Big jobs are scary.",
        "Robots get tired with HUGE asks.",
        "Chop the job into small steps.",
        "Tiny steps win every time!",
    ],
    "hints": {
        "tier1": {"highlight": "small steps"},
        "tier2": {"rephrase": "Order the small steps a robot would take to make a game."},
        "tier3": {"nudge": "First a hero. Then a world. Then add stuff. Then a way to win."},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Chop 'make a game' into 5 little steps:",
            "steps": [
                "Pick a hero",
                "Build the world",
                "Add things to do",
                "Add a way to win",
                "Test the game",
            ],
        },
    },
})

write("lesson_22_ask_again.json", {
    "id": 22, "chapter": "ch4",
    "title": "Ask Again When It's Wrong",
    "goal": "If the answer is wrong, say WHAT was wrong.",
    "sticker_emoji": "🔄",
    "mascot_lines": [
        "Sometimes the robot gets it wrong.",
        "Don't just say 'no'.",
        "Tell the robot WHAT is wrong.",
        "And give it a new try!",
    ],
    "hints": {
        "tier1": {"highlight": "what is wrong"},
        "tier2": {"rephrase": "Pick the answer that tells the robot WHAT to fix."},
        "tier3": {"nudge": "Vague: 'wrong'. Better: 'too big, make it small'."},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Robot drew a HUGE star. You wanted small. Which reply is best?",
            "choices": [
                {"label": "Wrong!", "right": False},
                {"label": "Make it small, half the size, please.", "right": True},
                {"label": "No.", "right": False},
                {"label": "Try again.", "right": False},
            ],
        },
    },
})

# === Chapter 5 — Memory & Spells ============================================

write("lesson_24_robot_memory.json", {
    "id": 24, "chapter": "ch5",
    "title": "The Robot's Memory Book",
    "goal": "A file called CLAUDE.md is a memory the robot reads first.",
    "sticker_emoji": "📓",
    "mascot_lines": [
        "Robots forget. They have tiny memories.",
        "But! You can give them a memory BOOK.",
        "Grown-ups call it CLAUDE.md.",
        "The robot reads it every time. So it never forgets your rules!",
    ],
    "hints": {
        "tier1": {"highlight": "memory"},
        "tier2": {"rephrase": "Stack three rules into a pretend memory book."},
        "tier3": {"nudge": "Each block is one rule the robot will remember forever."},
    },
    "game": {
        "type": "place-blocks",
        "payload": {
            "prompt": "Build a memory book by stacking rules in order:",
            "blocks": ["I LIKE DOGS", "USE SHORT WORDS", "ALWAYS BE KIND"],
            "solution": ["I LIKE DOGS", "USE SHORT WORDS", "ALWAYS BE KIND"],
        },
    },
})

write("lesson_25_my_memory_rules.json", {
    "id": 25, "chapter": "ch5",
    "title": "Write My Own Memory Rules",
    "goal": "Add your own rule and watch the robot remember.",
    "sticker_emoji": "✍️",
    "mascot_lines": [
        "Your turn! Pick a rule for the robot.",
        "Type it short and clear.",
        "Then the robot will remember it forever.",
        "Try a color you like!",
    ],
    "hints": {
        "tier1": {"highlight": "favorite color"},
        "tier2": {"rephrase": "Type a sentence about your favorite color."},
        "tier3": {"nudge": "Try: 'My favorite color is blue' (or any color you like!)."},
    },
    "game": {
        "type": "type-this-word",
        "payload": {
            "prompt": "Type a rule about your favorite color:",
            "target_display": "My favorite color is _____",
            "targets": ["color is", "color"],
            "hint_wrong": "Use the word 'color' in your sentence.",
        },
    },
})

write("lesson_26_magic_spells.json", {
    "id": 26, "chapter": "ch5",
    "title": "Skills Are Magic Spells",
    "goal": "A skill is a special trick the robot can learn.",
    "sticker_emoji": "🪄",
    "mascot_lines": [
        "Robots can learn special tricks.",
        "We call them SKILLS. Like magic spells!",
        "/draw = make a picture.",
        "/save = put it in the cloud.",
        "/loop = do it again and again.",
    ],
    "hints": {
        "tier1": {"highlight": "magic word"},
        "tier2": {"rephrase": "Each spell starts with a / and does a special job. Match them!"},
        "tier3": {"nudge": "/draw makes pictures. /save sends to cloud. /loop repeats."},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "Match each magic word to its job:",
            "pairs": [
                {"left": "/draw", "right": "Make a picture"},
                {"left": "/save", "right": "Push to cloud"},
                {"left": "/loop", "right": "Do it again and again"},
                {"left": "/read", "right": "Read out loud"},
            ],
        },
    },
})

write("lesson_27_make_a_skill.json", {
    "id": 27, "chapter": "ch5",
    "title": "Make Your Own Spell",
    "goal": "Give your spell a name, a job, and steps.",
    "sticker_emoji": "🎩",
    "mascot_lines": [
        "Want to make your OWN spell?",
        "First: pick a name. Like /smile.",
        "Then: tell when to use it.",
        "Then: list the steps it does.",
        "BOOM. Custom spell unlocked!",
    ],
    "hints": {
        "tier1": {"highlight": "order"},
        "tier2": {"rephrase": "Order the parts you write to make a spell."},
        "tier3": {"nudge": "First name, then when, then steps. The spell needs all three!"},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Order the parts of a spell:",
            "steps": ["Name (like /smile)", "When to use it", "Steps it does", "Done!"],
        },
    },
})

# === Chapter 6 — When Things Break (3 net new) ==============================

write("lesson_29_read_the_error.json", {
    "id": 29, "chapter": "ch6",
    "title": "Read the Red Words",
    "goal": "Errors are clues, not yelling.",
    "sticker_emoji": "🟥",
    "mascot_lines": [
        "When things break, the screen turns RED.",
        "Don't panic! Red words are CLUES.",
        "They tell you what part broke.",
        "Read them slow. Find the helper word.",
    ],
    "hints": {
        "tier1": {"highlight": "name"},
        "tier2": {"rephrase": "Find the part that names the problem."},
        "tier3": {"nudge": "Look for words like 'NameError' or 'is not defined' — those name the problem!"},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which part of this error names the problem?\n\"NameError: 'kitten' is not defined on line 3\"",
            "choices": [
                {"label": "line 3", "right": False},
                {"label": "NameError", "right": True},
                {"label": "kitten", "right": False},
                {"label": "is not defined", "right": False},
            ],
        },
    },
})

write("lesson_30_tell_what_happened.json", {
    "id": 30, "chapter": "ch6",
    "title": "Tell the Robot What Happened",
    "goal": "'It crashed' is fuzzy. Add WHAT and WHEN.",
    "sticker_emoji": "📣",
    "mascot_lines": [
        "When you tell a grown-up about a bug,",
        "say WHAT happened, and WHEN.",
        "Not just 'it crashed'.",
        "But: 'it crashed when I clicked Save'.",
        "WAY more useful for fixing!",
    ],
    "hints": {
        "tier1": {"highlight": "WHEN"},
        "tier2": {"rephrase": "Pick the bug report that tells WHAT and WHEN."},
        "tier3": {"nudge": "Look for two things: a thing that broke, AND a thing the kid did."},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which bug report is best?",
            "choices": [
                {"label": "It is broken!", "right": False},
                {"label": "Help.", "right": False},
                {"label": "The score went to zero when I touched a coin.", "right": True},
                {"label": "Idk what happened.", "right": False},
            ],
        },
    },
})

write("lesson_31_try_a_different_way.json", {
    "id": 31, "chapter": "ch6",
    "title": "Try a Different Way",
    "goal": "If one path is blocked, ask for another.",
    "sticker_emoji": "🛤️",
    "mascot_lines": [
        "Stuck? Don't bash your head!",
        "Tell the robot: 'let's try a different way'.",
        "It will try a NEW path.",
        "There is always more than one road.",
    ],
    "hints": {
        "tier1": {"highlight": "different"},
        "tier2": {"rephrase": "Pick the reply that asks the robot for a NEW way."},
        "tier3": {"nudge": "The phrase 'let's try a different way' is a magic unsticker!"},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "First way did not work. What do you say next?",
            "choices": [
                {"label": "I quit!", "right": False},
                {"label": "Let's try a different way.", "right": True},
                {"label": "Same thing again, please.", "right": False},
                {"label": "...", "right": False},
            ],
        },
    },
})

# === Chapter 7 — Make a Game (10 net new) ===================================

write("lesson_32_what_is_a_world.json", {
    "id": 32, "chapter": "ch7",
    "title": "What Is a Game World?",
    "goal": "A world is a stage with a floor, sky, and stuff.",
    "sticker_emoji": "🌍",
    "mascot_lines": [
        "A game world is like a tiny stage.",
        "There is a floor to walk on.",
        "A sky above. Maybe some clouds.",
        "And stuff to bump into and grab!",
    ],
    "hints": {
        "tier1": {"highlight": "parts"},
        "tier2": {"rephrase": "Pick the part that is NOT in a normal game world."},
        "tier3": {"nudge": "Floor, sky, hero, blocks — all in. What does NOT belong?"},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which is NOT a part of a game world?",
            "choices": [
                {"label": "Floor", "right": False},
                {"label": "Sky", "right": False},
                {"label": "Hero", "right": False},
                {"label": "Math homework", "right": True},
            ],
        },
    },
})

write("lesson_33_input_action_result.json", {
    "id": 33, "chapter": "ch7",
    "title": "Press, Move, Happen",
    "goal": "Input → action → result. That's a game.",
    "sticker_emoji": "🎮",
    "mascot_lines": [
        "Every game is the same shape:",
        "You PRESS. Hero MOVES. Something HAPPENS.",
        "Press right. Hero walks right.",
        "Bump a coin. Score goes up!",
        "Three steps. Always the same.",
    ],
    "hints": {
        "tier1": {"highlight": "order"},
        "tier2": {"rephrase": "Order the three steps: input, action, result."},
        "tier3": {"nudge": "First the kid does something. Then the hero. Then the game!"},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Order: press, move, happen.",
            "steps": ["Press the right arrow", "Hero moves right", "Hero touches a coin", "Score goes up!"],
        },
    },
})

write("lesson_34_sprites_and_costumes.json", {
    "id": 34, "chapter": "ch7",
    "title": "Sprites and Costumes",
    "goal": "A sprite is a little picture that has a job.",
    "sticker_emoji": "🐱",
    "mascot_lines": [
        "A sprite is a tiny picture in a game.",
        "The hero is a sprite. Coins are sprites. Bad guys are sprites.",
        "Each sprite has a costume — what it looks like.",
        "Same sprite can have many costumes!",
    ],
    "hints": {
        "tier1": {"highlight": "costume"},
        "tier2": {"rephrase": "Match each sprite to its job in the game."},
        "tier3": {"nudge": "Hero walks. Coin gives points. Bad guy hurts. Floor holds you up."},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "Match the sprite to its job:",
            "pairs": [
                {"left": "🦸 Hero", "right": "Walks and jumps"},
                {"left": "🪙 Coin", "right": "Adds score"},
                {"left": "👾 Bad guy", "right": "Takes a heart"},
                {"left": "🟫 Brick", "right": "Holds you up"},
            ],
        },
    },
})

write("lesson_35_move_my_hero.json", {
    "id": 35, "chapter": "ch7",
    "title": "Move My Hero",
    "goal": "Use arrow keys to walk a hero around a stage.",
    "sticker_emoji": "🏃",
    "mascot_lines": [
        "TIME TO MOVE!",
        "Use the arrow keys.",
        "Left arrow = walk left. Right arrow = walk right.",
        "Reach the FLAG to win!",
    ],
    "hints": {
        "tier1": {"highlight": "arrow"},
        "tier2": {"rephrase": "Click on the game first, then press the right arrow key."},
        "tier3": {"nudge": "Right arrow → hero goes right. Hold it down to keep going!"},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which key moves the hero RIGHT?",
            "choices": [
                {"label": "← Left arrow", "right": False},
                {"label": "→ Right arrow", "right": True},
                {"label": "↑ Up arrow", "right": False},
                {"label": "Q key", "right": False},
            ],
        },
    },
})

write("lesson_36_hitboxes.json", {
    "id": 36, "chapter": "ch7",
    "title": "Invisible Hitboxes",
    "goal": "A hitbox is the see-through square that bumps.",
    "sticker_emoji": "📦",
    "mascot_lines": [
        "Look closely!",
        "Around every sprite is an invisible BOX.",
        "It is called a HITBOX.",
        "When two hitboxes touch — BUMP!",
        "Hitboxes are how the game knows things touched.",
    ],
    "hints": {
        "tier1": {"highlight": "touch"},
        "tier2": {"rephrase": "A hitbox is invisible, but it makes things bump. Pick the true thing."},
        "tier3": {"nudge": "Hitboxes are squares around sprites that the game uses to detect bumps."},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "What is a hitbox?",
            "choices": [
                {"label": "A real picture you can see", "right": False},
                {"label": "An invisible square that bumps things", "right": True},
                {"label": "A song the game plays", "right": False},
                {"label": "A place to keep snacks", "right": False},
            ],
        },
    },
})

write("lesson_37_gravity.json", {
    "id": 37, "chapter": "ch7",
    "title": "Falling Down: Gravity",
    "goal": "Gravity pulls the hero down unless something holds them.",
    "sticker_emoji": "⬇️",
    "mascot_lines": [
        "Drop a ball. It falls.",
        "Why? GRAVITY!",
        "Games have pretend gravity too.",
        "If nothing holds the hero up, they FALL.",
        "The floor holds them. So do bricks.",
    ],
    "hints": {
        "tier1": {"highlight": "gravity"},
        "tier2": {"rephrase": "Order the steps when a hero walks off a platform edge."},
        "tier3": {"nudge": "First the floor ends. Then gravity kicks in. Then the hero falls. Then they land!"},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Hero walked off the edge. Order what happens:",
            "steps": [
                "The floor stops",
                "Gravity pulls down",
                "Hero falls",
                "Hero lands on lower floor",
            ],
        },
    },
})

write("lesson_38_score_lives.json", {
    "id": 38, "chapter": "ch7",
    "title": "Score, Lives, and Hearts",
    "goal": "Win adds points. Lose takes a heart.",
    "sticker_emoji": "❤️",
    "mascot_lines": [
        "Two big numbers in most games:",
        "SCORE goes up when you do good things.",
        "LIVES (or hearts) go down when you mess up.",
        "Lose all hearts? Game over!",
        "Get points, save hearts. That's the trick!",
    ],
    "hints": {
        "tier1": {"highlight": "heart"},
        "tier2": {"rephrase": "Match each thing that happens to what changes."},
        "tier3": {"nudge": "Coin → score up. Spike → heart down. Win flag → win!"},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "Match each game event to what changes:",
            "pairs": [
                {"left": "🪙 Grab a coin", "right": "Score +1"},
                {"left": "🌵 Touch a spike", "right": "Heart -1"},
                {"left": "🚩 Reach the flag", "right": "You win!"},
                {"left": "💚 Find a 1UP mushroom", "right": "+1 extra life"},
            ],
        },
    },
})

write("lesson_39_levels.json", {
    "id": 39, "chapter": "ch7",
    "title": "Build a Level",
    "goal": "A level is a layout of blocks, coins, and bad guys.",
    "sticker_emoji": "🗺️",
    "mascot_lines": [
        "A level is the SHAPE of the world.",
        "Where the floor is. Where the coins go.",
        "Where the bad guys hide.",
        "Designers PAINT levels on a grid.",
        "You can paint your own!",
    ],
    "hints": {
        "tier1": {"highlight": "order"},
        "tier2": {"rephrase": "Order the steps to build a fun level."},
        "tier3": {"nudge": "First make the floor. Then add stuff. Then test. Then fix what is too hard!"},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Order the steps to build a level:",
            "steps": [
                "Make the floor",
                "Add coins to grab",
                "Add bad guys",
                "Add a flag at the end",
                "Play it and fix what is too hard",
            ],
        },
    },
})

write("lesson_40_win_lose.json", {
    "id": 40, "chapter": "ch7",
    "title": "Win Screen, Lose Screen",
    "goal": "Every game needs a way to end.",
    "sticker_emoji": "🏁",
    "mascot_lines": [
        "Games need to END.",
        "If you reach the flag — WIN screen!",
        "If hearts run out — LOSE screen.",
        "If time runs out — LOSE screen.",
        "Pick the right ending for each thing!",
    ],
    "hints": {
        "tier1": {"highlight": "ending"},
        "tier2": {"rephrase": "Match each game ending to the screen it shows."},
        "tier3": {"nudge": "Reaching the flag = win. Out of hearts = lose. Out of time = lose."},
    },
    "game": {
        "type": "drag-to-match",
        "payload": {
            "prompt": "Match each ending to the screen it shows:",
            "pairs": [
                {"left": "🚩 Reached the flag", "right": "Win screen"},
                {"left": "💔 Hearts at zero", "right": "Lose screen"},
                {"left": "⏱️ Out of time", "right": "Lose screen"},
            ],
        },
    },
})

write("lesson_41_polish.json", {
    "id": 41, "chapter": "ch7",
    "title": "Make It Feel Good",
    "goal": "Wiggles, sounds, and flashes make a game feel alive.",
    "sticker_emoji": "✨",
    "mascot_lines": [
        "Polish is the secret sauce.",
        "Tiny wiggles when the hero jumps.",
        "Boing sounds. Sparkles when you score.",
        "Same game, but feels SO much better!",
    ],
    "hints": {
        "tier1": {"highlight": "polish"},
        "tier2": {"rephrase": "Pick the part that is POLISH, not core gameplay."},
        "tier3": {"nudge": "Sounds, sparkles, wiggles — these are extras that make it feel good!"},
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which one is POLISH (not core gameplay)?",
            "choices": [
                {"label": "Hero can walk", "right": False},
                {"label": "Boing sound when you jump", "right": True},
                {"label": "Score goes up", "right": False},
                {"label": "Coin makes points", "right": False},
            ],
        },
    },
})

# === Chapter 8 — Ship It (4 net new — existing 43, 47, 48 already shipped) ==

write("lesson_42_idea_to_plan.json", {
    "id": 42, "chapter": "ch8",
    "title": "Turn an Idea Into a Plan",
    "goal": "Big dreams become 5 little steps.",
    "sticker_emoji": "📋",
    "mascot_lines": [
        "You have a BIG idea.",
        "Don't try to build it all at once.",
        "Chop it into 5 small steps.",
        "Do them in order. Done!",
    ],
    "hints": {
        "tier1": {"highlight": "order"},
        "tier2": {"rephrase": "Order the steps from idea to finished game."},
        "tier3": {"nudge": "Idea first. Then plan. Then build. Then test. Then SHARE!"},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Order the steps from idea to ship:",
            "steps": [
                "Have the idea",
                "Make a 5-step plan",
                "Build step 1",
                "Test it",
                "Share with someone",
            ],
        },
    },
})

write("lesson_44_level_editor.json", {
    "id": 44, "chapter": "ch8",
    "title": "Level Editor Capstone",
    "goal": "Build YOUR level. Save it. Play it.",
    "sticker_emoji": "🛠️",
    "mascot_lines": [
        "TIME TO BUILD YOUR OWN LEVEL.",
        "Pick floor blocks, coins, spikes, a flag.",
        "Make it fun. Make it tricky.",
        "Then PLAY it!",
    ],
    "hints": {
        "tier1": {"highlight": "fun"},
        "tier2": {"rephrase": "Order the steps to make a good level."},
        "tier3": {"nudge": "Floor first. Then coins to grab. Then a challenge. Then a flag at the end!"},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Order the level-building steps:",
            "steps": [
                "Place the floor blocks",
                "Add 5 coins to grab",
                "Add 1 spike for a challenge",
                "Add a flag at the end",
            ],
        },
    },
})

write("lesson_45_ask_ai_for_feature.json", {
    "id": 45, "chapter": "ch8",
    "title": "Ask AI to Add a Feature",
    "goal": "Tell Claude what feature you want. Pick the best plan.",
    "sticker_emoji": "💡",
    "mascot_lines": [
        "Want a new thing in your game?",
        "Just ASK!",
        "Tell Claude what you want.",
        "Claude will give you a plan.",
        "Pick the plan that fits your game best!",
    ],
    "hints": {
        "tier1": {"highlight": "double jump"},
        "tier2": {"rephrase": "Pick the request that gives Claude the most clear feature idea."},
        "tier3": {"nudge": "More words about the feature = better plan from Claude!"},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Try asking Claude to plan a 'double jump' or 'speed boost' feature.",
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Which message asks Claude best for a new feature?",
            "choices": [
                {"label": "Stuff.", "right": False},
                {"label": "Plan a double-jump for my hero with a small wiggle.", "right": True},
                {"label": "Make it cooler.", "right": False},
                {"label": "Idk.", "right": False},
            ],
        },
    },
})

write("lesson_46_my_first_platformer.json", {
    "id": 46, "chapter": "ch8",
    "title": "My First Platformer",
    "goal": "Combine sprite, hitbox, gravity, score, and 1 level.",
    "sticker_emoji": "🦘",
    "mascot_lines": [
        "TIME FOR THE BIG ONE.",
        "Take everything you learned.",
        "Sprite. Hitbox. Gravity. Score. Level.",
        "Mix them all into ONE game.",
        "You. Are. A. Builder.",
    ],
    "hints": {
        "tier1": {"highlight": "order"},
        "tier2": {"rephrase": "Order the steps to make a platformer game."},
        "tier3": {"nudge": "Hero first. Then world. Then physics. Then score. Then test!"},
    },
    "game": {
        "type": "sequence-the-steps",
        "payload": {
            "prompt": "Build a platformer. Order the steps:",
            "steps": [
                "Pick a hero sprite",
                "Build the level",
                "Turn on gravity",
                "Add score and lives",
                "Test the game",
            ],
        },
    },
})

# === Chapter 9 — The Big Build (the secret) =================================
# IMPORTANT: NO Mario / plumber / Bowser / Peach references in lesson 49-54.
# Lesson 55 cinematic does the reveal — it lives in assets/cinematic/finale.html.

write("lesson_49_the_wish.json", {
    "id": 49, "chapter": "ch9",
    "title": "The Wish",
    "goal": "Tell the AI what kind of game you want to make.",
    "sticker_emoji": "🌟",
    "mascot_lines": [
        "Last chapter! THIS is where it all comes together.",
        "We are going to make a REAL game.",
        "First, you have to tell the AI what you want.",
        "What kind of game? What can the hero do?",
    ],
    "hints": {
        "tier1": {"highlight": "jump"},
        "tier2": {"rephrase": "Type a wish that includes 'jump' and 'world'."},
        "tier3": {"nudge": "Try: 'I want a hero who can run and jump in a world with levels'."},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Tell Claude what kind of game you want!",
    },
    "game": {
        "type": "type-this-word",
        "payload": {
            "prompt": "Tell Claude your wish. Use the word 'jump' in your message:",
            "target_display": "I want a hero who can ___ and ___ in a world with ___",
            "targets": ["jump"],
            "hint_wrong": "Use the word 'jump' somewhere in your wish.",
        },
    },
})

write("lesson_50_iter1_hero_floor.json", {
    "id": 50, "chapter": "ch9",
    "title": "Iteration 1: Hero & Floor",
    "goal": "Bug! The hero falls through the world. Fix the floor.",
    "sticker_emoji": "🧱",
    "mascot_lines": [
        "Claude built version one.",
        "Uh oh — the hero falls FOREVER.",
        "The collision with the floor is wrong.",
        "Ask Claude what's wrong. Then pick the fix.",
    ],
    "hints": {
        "tier1": {"highlight": "floor"},
        "tier2": {"rephrase": "The bug is about the floor. Pick the fix that adds floor collision."},
        "tier3": {"nudge": "The hero needs to STOP when it touches the floor. Look for 'stop on floor'."},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Ask: 'why does my hero fall forever?'",
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Hero falls forever. Pick the fix:",
            "choices": [
                {"label": "Make the hero blue", "right": False},
                {"label": "Add: stop the hero when it touches the floor", "right": True},
                {"label": "Remove the floor", "right": False},
                {"label": "Add more coins", "right": False},
            ],
        },
    },
})

write("lesson_51_iter2_jump.json", {
    "id": 51, "chapter": "ch9",
    "title": "Iteration 2: Jump",
    "goal": "Bug! The hero floats up forever. Fix the jump.",
    "sticker_emoji": "🦘",
    "mascot_lines": [
        "Now we add jump.",
        "BUG: hero floats up forever when you hold the arrow.",
        "A jump should be ONE push, not a forever push.",
        "Then gravity wins.",
    ],
    "hints": {
        "tier1": {"highlight": "one push"},
        "tier2": {"rephrase": "A jump happens ONCE per press. Pick the right description."},
        "tier3": {"nudge": "Jump is a one-time push UP. After that, gravity wins!"},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Ask: 'why does my hero float up forever?'",
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Pick the right way a jump should work:",
            "choices": [
                {"label": "Hero goes up forever while you hold the arrow", "right": False},
                {"label": "Hero gets ONE big push up, then falls back down", "right": True},
                {"label": "Hero teleports to the sky", "right": False},
                {"label": "Hero goes sideways", "right": False},
            ],
        },
    },
})

write("lesson_52_iter3_coins_score.json", {
    "id": 52, "chapter": "ch9",
    "title": "Iteration 3: Coins & Score",
    "goal": "Bug! The coin stays after pickup. Fix it.",
    "sticker_emoji": "🪙",
    "mascot_lines": [
        "Now we add coins!",
        "BUG: pick up a coin, score goes up, but the coin STAYS.",
        "So the score keeps going up forever!",
        "Need to make the coin disappear when grabbed.",
    ],
    "hints": {
        "tier1": {"highlight": "disappear"},
        "tier2": {"rephrase": "Pick the fix that makes the coin go away after pickup."},
        "tier3": {"nudge": "Look for words like 'remove' or 'disappear' or 'hide' the coin."},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Ask: 'why does my coin stay after I pick it up?'",
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Coin gives score but stays forever. Pick the fix:",
            "choices": [
                {"label": "Make the coin smaller", "right": False},
                {"label": "Remove the coin from the world after pickup", "right": True},
                {"label": "Add more coins", "right": False},
                {"label": "Make the coin sing", "right": False},
            ],
        },
    },
})

write("lesson_53_iter4_bad_guy.json", {
    "id": 53, "chapter": "ch9",
    "title": "Iteration 4: Bad Guy",
    "goal": "Bug! The bad guy walks off the edge. Fix patrol.",
    "sticker_emoji": "👾",
    "mascot_lines": [
        "Now we add a bad guy. It walks left and right.",
        "BUG: it walks RIGHT OFF the platform!",
        "It needs to TURN AROUND when it sees the edge.",
    ],
    "hints": {
        "tier1": {"highlight": "turn around"},
        "tier2": {"rephrase": "Pick the rule that makes the bad guy turn at edges."},
        "tier3": {"nudge": "Look for 'if next tile is empty, turn around'."},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Ask: 'why does my bad guy fall off the edge?'",
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Bad guy walks off the edge. Pick the fix:",
            "choices": [
                {"label": "Make it invisible", "right": False},
                {"label": "If the next tile is empty, turn around", "right": True},
                {"label": "Make it jump", "right": False},
                {"label": "Move the floor", "right": False},
            ],
        },
    },
})

write("lesson_54_iter5_powerup.json", {
    "id": 54, "chapter": "ch9",
    "title": "Iteration 5: Power-Up",
    "goal": "Bug! Power-up stays after death. Reset on death.",
    "sticker_emoji": "🌟",
    "mascot_lines": [
        "We added a power-up! Hero gets BIGGER.",
        "BUG: hero loses a heart, but stays big forever!",
        "Power-up should reset when hero dies.",
    ],
    "hints": {
        "tier1": {"highlight": "reset"},
        "tier2": {"rephrase": "Pick the fix that makes the hero shrink back when they die."},
        "tier3": {"nudge": "Look for 'reset to small on death'."},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Ask: 'why does my hero stay big after dying?'",
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Hero stays big after dying. Pick the fix:",
            "choices": [
                {"label": "Reset hero to small when they lose a heart", "right": True},
                {"label": "Make the hero glow", "right": False},
                {"label": "Remove the power-up forever", "right": False},
                {"label": "Add more hearts", "right": False},
            ],
        },
    },
})

# Lesson 55 is the cinematic-trigger lesson. Game mechanic is minimal — the magic
# is in the cinematic page launched at success. Note: NO mario/plumber/peach text.
write("lesson_55_iter6_flag_reveal.json", {
    "id": 55, "chapter": "ch9",
    "title": "Iteration 6: Flag & Finish",
    "goal": "Last bug! The flag fires too early. Fix collision. Then... see what you built.",
    "sticker_emoji": "🚩",
    "mascot_lines": [
        "LAST iteration! We add the flag.",
        "BUG: flag fires when you JUST walk past it.",
        "It should only fire when you TOUCH it.",
        "After we fix this... look what we made together.",
    ],
    "hints": {
        "tier1": {"highlight": "touch"},
        "tier2": {"rephrase": "Pick the fix that makes the flag fire only on touch."},
        "tier3": {"nudge": "The flag needs proper hitbox-on-hitbox checking — not just 'walked past'."},
    },
    "sandbox": {
        "helpers": ["claude"],
        "hint": "Ask: 'why does my flag fire when I just walk past it?'",
    },
    "game": {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Flag fires too early. Pick the fix:",
            "choices": [
                {"label": "Use real hitbox-on-hitbox collision", "right": True},
                {"label": "Make the flag bigger", "right": False},
                {"label": "Make the flag invisible", "right": False},
                {"label": "Remove the flag", "right": False},
            ],
        },
    },
})

log.info("Authored %d new lesson JSONs", 45)
