"""Expand every lesson_NN_*.json into the v2 (questions[] + variations[]) schema.

Schema goes from:
    { game: {type, payload}, hints: ... }
to:
    { game: {...},                       # kept for legacy/back-compat
      questions: [
        { id, interaction:{type,payload}, variations:[{prompt, options:[{text,correct}]}, x5] },
        ...
      ],
      hints: ... }

questions[0].interaction = the original lesson.game (the demonstration).
questions[1..N] get small rotating gate interactions (tap/type/drag) so
the kid can't speed-pick without engaging.

5 variations per question, 5 question slots per lesson → 25 MCQs per lesson
× 60 lessons = 1500 unique MCQ entries. Variations are produced from a
per-lesson seed (5 right facts × 5 wrong distractors) crossed with 5
question frames × 5 prompt paraphrases.

Idempotent: safe to re-run. Overwrites lesson JSON in place.
"""
from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("expand-lessons-v2")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"

# ----------------------------------------------------------------------------
# Per-lesson seed data. Each lesson contributes:
#   concept : short noun phrase used in question frames ("a computer")
#   facts   : 5 short kid-friendly TRUE statements (each a complete sentence)
#   wrongs  : 5 short FALSE statements that sound plausible to a 7yo
# Generator combines these with 5 frames × 5 paraphrases to produce 25 MCQs.
# ----------------------------------------------------------------------------

SEEDS: dict[int, dict[str, Any]] = {
    1: {
        "concept": "a computer",
        "facts": [
            "A computer is a smart helper.",
            "A computer only does what we tell it.",
            "A laptop is a computer.",
            "Computers do not guess what we want.",
            "A phone is a tiny computer.",
        ],
        "wrongs": [
            "A computer can read your mind.",
            "A computer is a kind of tree.",
            "A computer always knows what is best.",
            "Computers feel sad when you turn them off.",
            "A computer grows on a farm.",
        ],
    },
    2: {
        "concept": "talking to Claude",
        "facts": [
            "Claude is a helper made of words.",
            "We type words to ask Claude for help.",
            "Claude waits for you to finish typing.",
            "Claude works best when you say what you want.",
            "Claude can help you make and learn things.",
        ],
        "wrongs": [
            "Claude lives in your fridge.",
            "Claude can hear you yelling at it.",
            "Claude is a real puppy.",
            "Claude only works on Tuesdays.",
            "Claude reads your dreams.",
        ],
    },
    3: {
        "concept": "magic boxes (variables)",
        "facts": [
            "A box can hold one thing at a time.",
            "We give boxes names so we can find them.",
            "We can change what is inside a box.",
            "A box can hold a number or a word.",
            "Naming a box makes our code easy to read.",
        ],
        "wrongs": [
            "A box holds a thousand things at once.",
            "Boxes have to be square shaped.",
            "Boxes only hold candy.",
            "A box never lets you change what is inside.",
            "Boxes need to be fed every night.",
        ],
    },
    4: {
        "concept": "the sticky-note rule (memory)",
        "facts": [
            "Helpers forget when you close the chat.",
            "A sticky note tells the helper what to remember.",
            "Sticky notes are short and clear.",
            "Sticky notes go at the start of the chat.",
            "Sticky notes save us from saying things over and over.",
        ],
        "wrongs": [
            "Sticky notes can fly across the room.",
            "Helpers remember everything forever.",
            "Sticky notes only work on Mondays.",
            "Sticky notes are for the kid, not the helper.",
            "Sticky notes are made of cheese.",
        ],
    },
    5: {
        "concept": "math made of thinking",
        "facts": [
            "Computers do math super fast.",
            "Adding 1 + 1 always equals 2.",
            "We can use math to make rules.",
            "Math helps games count points.",
            "Computers never get bored of math.",
        ],
        "wrongs": [
            "Computers add numbers wrong on purpose.",
            "1 plus 1 sometimes equals 7.",
            "Math only works on paper.",
            "Computers fall asleep doing math.",
            "Numbers are afraid of computers.",
        ],
    },
    6: {
        "concept": "the Turing dream",
        "facts": [
            "Alan Turing dreamed of a thinking machine.",
            "He wrote rules so a machine could solve puzzles.",
            "Turing helped end a big war with code.",
            "His ideas led to today's computers.",
            "Turing imagined machines that could learn.",
        ],
        "wrongs": [
            "Turing was a singing chef.",
            "Turing built a flying horse.",
            "He invented bubble gum.",
            "He thought computers would never work.",
            "He lived on the moon.",
        ],
    },
    7: {
        "concept": "the perceptron pet",
        "facts": [
            "A perceptron is a tiny learning machine.",
            "It learns by looking at lots of examples.",
            "It says yes or no based on what it sees.",
            "It can be trained to spot a pattern.",
            "Many perceptrons together make a big brain.",
        ],
        "wrongs": [
            "A perceptron is a kind of cookie.",
            "Perceptrons learn by sleeping.",
            "A perceptron only says maybe.",
            "Perceptrons live inside our shoes.",
            "Perceptrons are made of water.",
        ],
    },
    8: {
        "concept": "back-and-forth learning",
        "facts": [
            "We learn by trying, missing, and trying again.",
            "Helpers learn from feedback we give them.",
            "Mistakes are clues that help us improve.",
            "Practice makes patterns easy to see.",
            "Asking is a strong way to learn.",
        ],
        "wrongs": [
            "If you fail once you should stop forever.",
            "Helpers learn nothing from feedback.",
            "Mistakes mean you are bad at it.",
            "Practice makes things harder.",
            "Asking questions is rude.",
        ],
    },
    9: {
        "concept": "word attention",
        "facts": [
            "Helpers pay attention to important words.",
            "Some words matter more than others.",
            "Attention helps the helper guess what is next.",
            "Big helpers look at many words at once.",
            "The right word can change the whole answer.",
        ],
        "wrongs": [
            "Helpers ignore every word equally.",
            "All words have the same meaning.",
            "Attention makes helpers slower.",
            "One word never changes anything.",
            "Helpers only read every other word.",
        ],
    },
    10: {
        "concept": "how an LLM is born",
        "facts": [
            "An LLM reads tons and tons of books and pages.",
            "It learns to guess the next word.",
            "Training takes lots of computers and time.",
            "The model gets better with more practice.",
            "After training, the model can chat with us.",
        ],
        "wrongs": [
            "An LLM is hatched from a real egg.",
            "Models train for one second and are done.",
            "Models read just one tiny book.",
            "An LLM is grown in a garden.",
            "Models train on Mars.",
        ],
    },
    11: {
        "concept": "Claude in depth",
        "facts": [
            "Claude is a careful helper who likes clear rules.",
            "You can give Claude a sticky-note style of rules.",
            "Claude works step by step on hard tasks.",
            "Claude can explain why it picked an answer.",
            "Claude can write code, stories, and plans.",
        ],
        "wrongs": [
            "Claude only speaks emoji.",
            "Claude refuses to follow rules.",
            "Claude works only when it rains.",
            "Claude only writes one word per day.",
            "Claude never explains anything.",
        ],
    },
    12: {
        "concept": "Cursor in depth",
        "facts": [
            "Cursor is a code editor with a helper inside.",
            "Cursor can change many files at once.",
            "We can talk to Cursor about the code we wrote.",
            "Cursor reads our project to help better.",
            "Cursor can explain bugs in plain words.",
        ],
        "wrongs": [
            "Cursor only changes the wallpaper.",
            "Cursor cannot read your project at all.",
            "Cursor speaks only in numbers.",
            "Cursor writes code only for video games.",
            "Cursor must be paid in stickers.",
        ],
    },
    13: {
        "concept": "Gemini in depth",
        "facts": [
            "Gemini is a helper made by Google.",
            "Gemini can look at pictures and words together.",
            "Gemini can answer using the web's facts.",
            "Gemini works on phones, tablets, and laptops.",
            "Gemini can help with school and play.",
        ],
        "wrongs": [
            "Gemini only works on a flip phone.",
            "Gemini cannot see pictures.",
            "Gemini eats batteries to wake up.",
            "Gemini only knows about clouds.",
            "Gemini speaks one word at a time.",
        ],
    },
    14: {
        "concept": "Codex in depth",
        "facts": [
            "Codex is a helper that is great at code.",
            "Codex can finish a line you started.",
            "Codex understands many programming languages.",
            "Codex helps fix small bugs fast.",
            "Codex is best when we say what we want.",
        ],
        "wrongs": [
            "Codex writes only in crayon.",
            "Codex only knows ten words.",
            "Codex hates code.",
            "Codex always picks the wrong answer.",
            "Codex is a real animal.",
        ],
    },
    15: {
        "concept": "OpenCode in depth",
        "facts": [
            "OpenCode is a helper that is open for everyone.",
            "Open tools can be checked by anyone.",
            "OpenCode can be run on your own computer.",
            "Sharing helps tools get better fast.",
            "Open tools are often free to use.",
        ],
        "wrongs": [
            "Open tools are always secret.",
            "OpenCode only works on Saturdays.",
            "Open tools cost a million dollars.",
            "Nobody is allowed to see open tools.",
            "Open tools turn off at sunset.",
        ],
    },
    16: {
        "concept": "Ollama on your computer",
        "facts": [
            "Ollama lets a helper live on your own laptop.",
            "Local helpers do not need the internet.",
            "Ollama keeps your words on your machine.",
            "We can pick which helper to load.",
            "Local helpers feel fast for small tasks.",
        ],
        "wrongs": [
            "Ollama needs a magic stone to work.",
            "Ollama copies your words to the moon.",
            "Local helpers only run online.",
            "Ollama always uses the slowest helper.",
            "Ollama eats your homework.",
        ],
    },
    17: {
        "concept": "picking the helper",
        "facts": [
            "Different helpers are good at different jobs.",
            "Pick a helper that fits the task.",
            "If one helper is stuck, ask another.",
            "Practice helps you know which to pick.",
            "Tell the helper what success looks like.",
        ],
        "wrongs": [
            "All helpers are exactly the same.",
            "Pick a helper by smell.",
            "Never switch helpers, ever.",
            "The helper picks YOU.",
            "Helpers only work on rainy days.",
        ],
    },
    18: {
        "concept": "ask, then build",
        "facts": [
            "Asking first saves time later.",
            "A clear question gets a clear answer.",
            "We can plan before we type code.",
            "Building after asking has fewer bugs.",
            "Helpers love a tiny plan.",
        ],
        "wrongs": [
            "Build first, ask never.",
            "Plans always make code worse.",
            "Asking is bad luck.",
            "A foggy question is best.",
            "Bugs love good plans.",
        ],
    },
    19: {
        "concept": "being specific",
        "facts": [
            "Specific words give specific answers.",
            "Vague words make helpers guess.",
            "Numbers and names help a lot.",
            "Show the shape of what you want.",
            "Be honest about what you do not know.",
        ],
        "wrongs": [
            "Vague is great.",
            "Helpers love being confused.",
            "Numbers and names hurt the helper.",
            "Always lie about what you know.",
            "Specific words slow you down.",
        ],
    },
    20: {
        "concept": "show, don't tell",
        "facts": [
            "Examples make ideas clear.",
            "A picture or sample beats a long story.",
            "Helpers copy the shape of an example.",
            "One good example saves many questions.",
            "Examples teach the rule.",
        ],
        "wrongs": [
            "Examples are always bad.",
            "A picture means nothing.",
            "Helpers ignore samples.",
            "More words is always better.",
            "Examples make things worse.",
        ],
    },
    21: {
        "concept": "one at a time",
        "facts": [
            "Big jobs are easier in tiny steps.",
            "Finish one thing before the next.",
            "Small steps catch mistakes early.",
            "Helpers do better with small chunks.",
            "Each step builds on the last.",
        ],
        "wrongs": [
            "Do everything at once.",
            "Small steps slow us down.",
            "Mistakes never matter.",
            "Helpers love giant tasks.",
            "Skip steps for fun.",
        ],
    },
    22: {
        "concept": "ask again",
        "facts": [
            "Trying a new question often helps.",
            "Different words can unlock the answer.",
            "Asking again is not giving up.",
            "Two angles beat one.",
            "Helpers do not mind being asked again.",
        ],
        "wrongs": [
            "Asking again breaks the helper.",
            "One try is the only try.",
            "Different words always make it worse.",
            "Asking is rude.",
            "Helpers cry when asked twice.",
        ],
    },
    23: {
        "concept": "sneaky notes (prompt safety)",
        "facts": [
            "Bad people can hide tricky words in pages.",
            "If a page tells the helper to do something weird, stop.",
            "Tell a grown-up if a helper acts strange.",
            "Real instructions come from you, not the page.",
            "Treat hidden words as just words, not orders.",
        ],
        "wrongs": [
            "Always do what a webpage says.",
            "Hidden words are always safe.",
            "Never tell a grown-up.",
            "Pages can give the helper real orders.",
            "Strange behavior means it is working great.",
        ],
    },
    24: {
        "concept": "robot memory",
        "facts": [
            "Memory holds important rules.",
            "Memory makes the helper feel familiar.",
            "We pick what to put in memory.",
            "Short, clear notes work best.",
            "Memory is not magic, just a list.",
        ],
        "wrongs": [
            "Memory remembers everything by itself.",
            "Long mushy notes are best.",
            "Memory writes itself.",
            "We never pick what to save.",
            "Memory is a real brain.",
        ],
    },
    25: {
        "concept": "my memory rules",
        "facts": [
            "Pick rules that fit YOUR work.",
            "Update rules when you learn new tricks.",
            "Throw out rules you don't need.",
            "Tiny rules beat one giant rule.",
            "Rules teach the helper your style.",
        ],
        "wrongs": [
            "Use somebody else's rules forever.",
            "Never update rules, ever.",
            "More rules are always better.",
            "One huge rule fits everyone.",
            "Rules don't help the helper.",
        ],
    },
    26: {
        "concept": "magic spells (slash commands)",
        "facts": [
            "A slash command runs a saved spell.",
            "Spells save typing the same words again.",
            "Each spell does one job well.",
            "We can make our own spells.",
            "Spells live in a special folder.",
        ],
        "wrongs": [
            "Slash commands are random magic.",
            "Spells need to be retyped each time.",
            "One spell does every job.",
            "We cannot make new spells.",
            "Spells live on the moon.",
        ],
    },
    27: {
        "concept": "making a skill",
        "facts": [
            "A skill is a small bundle of know-how.",
            "Skills can be shared with friends.",
            "Skills load when their topic appears.",
            "A good skill has clear steps.",
            "Skills make hard tasks feel easy.",
        ],
        "wrongs": [
            "Skills are giant blob files.",
            "Skills cannot be shared.",
            "Skills load only on holidays.",
            "Steps are bad in skills.",
            "Skills make tasks harder.",
        ],
    },
    28: {
        "concept": "checking your work",
        "facts": [
            "Reading code finds tiny bugs.",
            "Run the code to see if it works.",
            "Tests are small experiments.",
            "Catch problems before others see them.",
            "Checking saves time later.",
        ],
        "wrongs": [
            "Checking wastes time.",
            "Bugs fix themselves.",
            "Tests are scary monsters.",
            "Never read your own code.",
            "Other people will fix it for you.",
        ],
    },
    29: {
        "concept": "reading the error",
        "facts": [
            "Errors tell you where to look.",
            "Read the last line of an error first.",
            "Many errors are small typos.",
            "Errors are not scary, they are clues.",
            "Sharing the error helps the helper help you.",
        ],
        "wrongs": [
            "Errors are mean and useless.",
            "Skip the last line.",
            "Errors are always huge problems.",
            "Errors come from ghosts.",
            "Hide errors from the helper.",
        ],
    },
    30: {
        "concept": "telling what happened",
        "facts": [
            "Explain the steps you took.",
            "Say what you expected.",
            "Say what actually happened.",
            "Show the error or weird thing.",
            "A good story makes the bug easy to fix.",
        ],
        "wrongs": [
            "Skip the steps you took.",
            "Hide what you expected.",
            "Lie about what happened.",
            "Never share the error.",
            "Stories make bugs harder.",
        ],
    },
    31: {
        "concept": "trying a different way",
        "facts": [
            "If one path is stuck, try another.",
            "There is more than one way to solve a problem.",
            "Trying again is brave.",
            "A new angle finds new clues.",
            "Helpers can suggest other paths.",
        ],
        "wrongs": [
            "Only one way ever works.",
            "Trying again is for quitters.",
            "New angles never help.",
            "Helpers only know one path.",
            "Stuck means done forever.",
        ],
    },
    32: {
        "concept": "what is a world (in a game)",
        "facts": [
            "A world is the place a game happens.",
            "A world has rules like gravity.",
            "Worlds can be small or huge.",
            "We can change a world by changing its rules.",
            "Worlds need a hero to live in them.",
        ],
        "wrongs": [
            "A world has no rules at all.",
            "All worlds are the same size.",
            "Rules are stuck forever.",
            "Worlds never need a hero.",
            "Worlds are made of jelly.",
        ],
    },
    33: {
        "concept": "input, action, result",
        "facts": [
            "Input is what the player does.",
            "Action is what the game does next.",
            "Result is what the player sees.",
            "Every move follows this loop.",
            "A clear loop makes a clear game.",
        ],
        "wrongs": [
            "Input and result are the same.",
            "Games skip the action step.",
            "Loops are bad in games.",
            "Players never see the result.",
            "Action does nothing.",
        ],
    },
    34: {
        "concept": "sprites and costumes",
        "facts": [
            "A sprite is a picture in the game.",
            "Costumes are different looks for one sprite.",
            "Switching costumes makes movement.",
            "Sprites can be heroes or rocks.",
            "Sprites have a position on screen.",
        ],
        "wrongs": [
            "A sprite is a real ghost.",
            "Costumes never change.",
            "Sprites can never move.",
            "Only heroes are sprites.",
            "Sprites have no position.",
        ],
    },
    35: {
        "concept": "moving my hero",
        "facts": [
            "Pressing a key changes the hero's position.",
            "Speed is how fast the hero moves.",
            "We add to position to move right.",
            "We subtract to move left.",
            "Movement runs every frame.",
        ],
        "wrongs": [
            "Keys never move heroes.",
            "Speed never matters.",
            "Adding moves you up only.",
            "Subtracting deletes the hero.",
            "Movement runs once and stops.",
        ],
    },
    36: {
        "concept": "hitboxes",
        "facts": [
            "A hitbox is the area that can collide.",
            "Hitboxes can be smaller than the picture.",
            "We use hitboxes to test for hits.",
            "Hitboxes can be circles or squares.",
            "Good hitboxes feel fair to the player.",
        ],
        "wrongs": [
            "A hitbox is a real cardboard box.",
            "Hitboxes must match the picture exactly.",
            "Hitboxes are decorations only.",
            "Hitboxes can only be triangles.",
            "Hitboxes never feel fair.",
        ],
    },
    37: {
        "concept": "gravity",
        "facts": [
            "Gravity pulls things down each frame.",
            "Without gravity heroes float forever.",
            "We add a tiny number to vertical speed.",
            "Standing on the ground stops gravity.",
            "Gravity makes jumps feel real.",
        ],
        "wrongs": [
            "Gravity pushes things up.",
            "Heroes always fall sideways.",
            "Gravity adds a giant number once.",
            "Standing on the ground makes you fall faster.",
            "Gravity makes jumps feel fake.",
        ],
    },
    38: {
        "concept": "score and lives",
        "facts": [
            "Score goes up when you do well.",
            "Lives go down when you get hit.",
            "Lives at zero ends the game.",
            "Score gives the player a goal.",
            "We show the score on screen.",
        ],
        "wrongs": [
            "Score and lives are the same thing.",
            "Score never changes.",
            "Lives at zero make the game easier.",
            "Goals are bad in games.",
            "Hide the score from the player.",
        ],
    },
    39: {
        "concept": "levels",
        "facts": [
            "A level is one chunk of the game.",
            "Levels usually get harder.",
            "Each level can have new pieces.",
            "Beating a level feels great.",
            "Levels keep games fresh.",
        ],
        "wrongs": [
            "Levels never change.",
            "All levels are the same difficulty.",
            "Levels never add new pieces.",
            "Beating a level feels bad.",
            "Levels make games stale.",
        ],
    },
    40: {
        "concept": "win and lose",
        "facts": [
            "Winning means you reached the goal.",
            "Losing means the rules said you stopped.",
            "Win and lose make a game a game.",
            "Clear rules make winning fair.",
            "Losing teaches us how to try again.",
        ],
        "wrongs": [
            "Winning means giving up.",
            "Losing has no rules.",
            "Games don't need win or lose.",
            "Fairness ruins a game.",
            "Losing teaches us nothing.",
        ],
    },
    41: {
        "concept": "polish",
        "facts": [
            "Polish is small touches that make things feel good.",
            "Sound, color, and shake count as polish.",
            "Polish comes after the basics work.",
            "A little polish goes far.",
            "Players notice polish without saying so.",
        ],
        "wrongs": [
            "Polish is the very first step.",
            "Polish never matters.",
            "Polish only means floors.",
            "More polish is always bad.",
            "Players hate polish.",
        ],
    },
    42: {
        "concept": "idea to plan",
        "facts": [
            "An idea is a wish for a thing.",
            "A plan is the steps to make it.",
            "Plans help us not get lost.",
            "Plans can change as we learn.",
            "Ideas without plans rarely ship.",
        ],
        "wrongs": [
            "An idea is the same as a plan.",
            "Plans never help.",
            "Plans must never change.",
            "Ideas always ship by themselves.",
            "A plan is bad luck.",
        ],
    },
    43: {
        "concept": "the color editor",
        "facts": [
            "We can pick colors using sliders.",
            "Colors are made from red, green, and blue.",
            "Saved colors can be used again.",
            "A color tool lets you preview the look.",
            "Colors set the mood of the game.",
        ],
        "wrongs": [
            "Colors are made from milk and bread.",
            "We can save zero colors.",
            "Previews never work.",
            "Color does not change mood.",
            "Sliders pick songs, not colors.",
        ],
    },
    44: {
        "concept": "the level editor",
        "facts": [
            "A level editor lets us place pieces.",
            "We can save and reload our level.",
            "Editors are tools that help us build faster.",
            "Editors save lots of typing.",
            "A level editor makes games fun to make.",
        ],
        "wrongs": [
            "Editors only work for printers.",
            "Levels can never be saved.",
            "Editors slow us way down.",
            "Editors require giant typing.",
            "Editors make game-making boring.",
        ],
    },
    45: {
        "concept": "asking AI for a feature",
        "facts": [
            "Be clear about what you want to add.",
            "Show the file or place where it goes.",
            "Say what should happen step by step.",
            "Test the new feature after you add it.",
            "Helpers do best with small features.",
        ],
        "wrongs": [
            "Be vague about everything.",
            "Hide the file from the helper.",
            "Skip testing the new feature.",
            "Add ten features at once.",
            "Helpers like giant features only.",
        ],
    },
    46: {
        "concept": "my first platformer",
        "facts": [
            "A platformer has a hero who jumps.",
            "Platforms are where the hero stands.",
            "Falling off is a way to lose.",
            "Coins or stars are common rewards.",
            "Reaching the flag often wins.",
        ],
        "wrongs": [
            "Platformers never have a hero.",
            "Platforms are decorations only.",
            "Falling off is a way to win.",
            "Rewards are bad.",
            "Flags are hidden forever.",
        ],
    },
    47: {
        "concept": "showing a friend",
        "facts": [
            "Sharing your work feels good.",
            "Friends can spot fresh ideas.",
            "A short demo is best.",
            "Listen to feedback kindly.",
            "Pick what to keep, leave the rest.",
        ],
        "wrongs": [
            "Hide your work from everyone.",
            "Friends always spoil it.",
            "Demos must be very long.",
            "Argue with every comment.",
            "Take every comment as a rule.",
        ],
    },
    48: {
        "concept": "save and share",
        "facts": [
            "Saving keeps your work safe.",
            "Sharing lets others play.",
            "A clear file name helps you find it.",
            "Backups protect your hard work.",
            "Shared games can come back better.",
        ],
        "wrongs": [
            "Saving deletes your work.",
            "Sharing breaks the file.",
            "File names do not matter.",
            "Backups are useless.",
            "Shared games rot.",
        ],
    },
    49: {
        "concept": "the wish",
        "facts": [
            "A wish is a starting idea.",
            "Wishes get clearer as you build.",
            "A small wish is easier to test.",
            "Wishes can change after you learn.",
            "Naming the wish helps the team.",
        ],
        "wrongs": [
            "A wish is the final answer.",
            "Wishes get muddier as you build.",
            "Big wishes are easier to test.",
            "Wishes must never change.",
            "Naming wishes is silly.",
        ],
    },
    50: {
        "concept": "iter 1: hero on the floor",
        "facts": [
            "Step one: put the hero somewhere.",
            "Step two: stop them from falling forever.",
            "A floor blocks the hero from falling.",
            "Test by running and watching the screen.",
            "Tiny steps catch tiny bugs.",
        ],
        "wrongs": [
            "Skip placing the hero.",
            "Let the hero fall forever.",
            "Floors are decoration only.",
            "Never test what you wrote.",
            "Tiny steps hide bugs.",
        ],
    },
    51: {
        "concept": "iter 2: jump",
        "facts": [
            "A jump moves the hero up for a moment.",
            "Gravity pulls the hero back down.",
            "Hold time decides how high.",
            "We jump only when we are on the ground.",
            "A good jump feels snappy.",
        ],
        "wrongs": [
            "Jumps move the hero sideways.",
            "Gravity pushes us up after a jump.",
            "Hold time does nothing.",
            "Jumping in the air is fine.",
            "A good jump feels slow.",
        ],
    },
    52: {
        "concept": "iter 3: coins and score",
        "facts": [
            "A coin gives points when touched.",
            "Score shows on the top of the screen.",
            "Each coin disappears after pickup.",
            "More coins means more reasons to explore.",
            "Coins make a happy sound.",
        ],
        "wrongs": [
            "Coins take points away.",
            "Score is invisible.",
            "Coins stay forever.",
            "Coins make exploring boring.",
            "Coins are silent always.",
        ],
    },
    53: {
        "concept": "iter 4: the bad guy",
        "facts": [
            "A bad guy moves on a path.",
            "Touching a bad guy can hurt the hero.",
            "Patterns help the player learn the bad guy.",
            "A bad guy can be jumped on or avoided.",
            "Bad guys add tension to the world.",
        ],
        "wrongs": [
            "Bad guys never move.",
            "Touching them gives points.",
            "Patterns ruin everything.",
            "Bad guys cannot be avoided.",
            "Bad guys remove tension.",
        ],
    },
    54: {
        "concept": "iter 5: power-up",
        "facts": [
            "Power-ups give the hero a boost.",
            "Boosts can be speed, size, or extra jumps.",
            "Power-ups are exciting to find.",
            "A power-up usually has a timer.",
            "Visual flash shows the power is active.",
        ],
        "wrongs": [
            "Power-ups slow the hero down.",
            "Boosts always take points away.",
            "Power-ups are boring.",
            "Power-ups last forever always.",
            "Visual flash is for ads only.",
        ],
    },
    55: {
        "concept": "iter 6: flag and reveal",
        "facts": [
            "A flag at the end says you win.",
            "Touching the flag triggers a reveal.",
            "A win screen feels great.",
            "Try to make the win moment fun.",
            "Sharing the win is a sweet ending.",
        ],
        "wrongs": [
            "Flags lose the game.",
            "Reveals are illegal.",
            "Win screens are sad.",
            "Win moments must be boring.",
            "Sharing the win ruins it.",
        ],
    },
    56: {
        "concept": "what is a good idea",
        "facts": [
            "A good idea solves a real problem.",
            "Good ideas are clear and small.",
            "Good ideas help someone.",
            "Good ideas can be tested.",
            "Good ideas feel exciting to try.",
        ],
        "wrongs": [
            "Good ideas solve nothing.",
            "Foggy giant ideas are best.",
            "A good idea helps no one.",
            "You can't test a good idea.",
            "Good ideas feel boring.",
        ],
    },
    57: {
        "concept": "listening for problems",
        "facts": [
            "Problems hide in everyday gripes.",
            "Listen for the words 'I wish' and 'I hate'.",
            "Write down the problem so you remember.",
            "Ask why the problem matters.",
            "Big problems often have small fixes.",
        ],
        "wrongs": [
            "Problems are always loud and obvious.",
            "Don't listen to anyone.",
            "Memory beats writing things down.",
            "Don't ask why.",
            "Big problems need only big fixes.",
        ],
    },
    58: {
        "concept": "idea spark",
        "facts": [
            "A spark is one tiny idea worth chasing.",
            "Sparks come from mixing two old things.",
            "Capture sparks fast — they fade.",
            "A spark plus a problem can be a project.",
            "Sparks are the start, not the end.",
        ],
        "wrongs": [
            "A spark is the final answer.",
            "Sparks come from one big copy.",
            "Sparks last forever in your head.",
            "Sparks can't help projects.",
            "Sparks are the end, not the start.",
        ],
    },
    59: {
        "concept": "picking the hook",
        "facts": [
            "A hook is the catchy first part.",
            "The hook makes people try your thing.",
            "Hooks should be honest, not tricky.",
            "Show the hook in the first few seconds.",
            "A hook can be a question or a wow.",
        ],
        "wrongs": [
            "A hook is the last part.",
            "Hooks scare people away.",
            "Hooks must trick people.",
            "Save the hook for the end.",
            "Hooks must be long stories.",
        ],
    },
    60: {
        "concept": "make your game",
        "facts": [
            "Pick one idea and start small.",
            "Build, test, and play your game often.",
            "Show it to a friend for feedback.",
            "Polish only after the basics work.",
            "Finishing teaches more than dreaming.",
        ],
        "wrongs": [
            "Pick ten ideas and start huge.",
            "Build only, never test or play.",
            "Hide it from everyone.",
            "Polish before the basics work.",
            "Dreaming finishes the game.",
        ],
    },
}


# ----------------------------------------------------------------------------
# Frames + paraphrases — combined with each lesson's seed to produce MCQs.
# ----------------------------------------------------------------------------

# Each frame: (prompt template, picks_correct: bool, header for variation)
# When picks_correct=False, the "correct" answer is a wrong fact (player picks
# the lie). We keep that flow simple by inverting the option's correct flag.
FRAMES: list[dict[str, Any]] = [
    {"key": "what_is",     "prompt": "What is {concept}?",                                   "pick_truth": True},
    {"key": "true_fact",   "prompt": "Which one is TRUE about {concept}?",                   "pick_truth": True},
    {"key": "spot_lie",    "prompt": "One of these is silly! Pick the WRONG one about {concept}.", "pick_truth": False},
    {"key": "best_say",    "prompt": "Bytey wants to teach a friend about {concept}. What should he say?", "pick_truth": True},
    {"key": "good_rule",   "prompt": "Which rule about {concept} is a GOOD rule?",           "pick_truth": True},
]

PARAPHRASES: list[str] = [
    "",
    "Quick! ",
    "Hey friend — ",
    "Bytey wonders: ",
    "Tell me — ",
]


def _shuffled(seq: list[Any], salt: int) -> list[Any]:
    out = seq.copy()
    random.Random(salt).shuffle(out)
    return out


def _pick_n(seq: list[str], n: int, salt: int) -> list[str]:
    return _shuffled(seq, salt)[:n]


def _build_variation(
    frame: dict[str, Any],
    paraphrase: str,
    seed: dict[str, Any],
    variation_idx: int,
    question_idx: int,
) -> dict[str, Any]:
    """One {prompt, options:[{text,correct}]*4} entry."""
    salt = (question_idx + 1) * 100 + variation_idx
    facts = seed["facts"]
    wrongs = seed["wrongs"]
    prompt = paraphrase + frame["prompt"].format(concept=seed["concept"])

    if frame["pick_truth"]:
        correct_text = facts[(variation_idx + question_idx) % len(facts)]
        wrong_texts = _pick_n(wrongs, 3, salt)
    else:
        # spot_lie: correct = a WRONG fact (the silly one)
        correct_text = wrongs[(variation_idx + question_idx) % len(wrongs)]
        wrong_texts = _pick_n(facts, 3, salt)

    options = [{"text": correct_text, "correct": True}]
    options.extend({"text": t, "correct": False} for t in wrong_texts)
    options = _shuffled(options, salt + 7)
    return {"prompt": prompt, "options": options}


# ----------------------------------------------------------------------------
# Gate interactions for Q1..QN. Q0 keeps the original lesson.game.
# ----------------------------------------------------------------------------

GATE_TEMPLATES: list[dict[str, Any]] = [
    {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Tap the orange dot to unlock the question!",
            "choices": [
                {"label": "🟠", "right": True},
                {"label": "🔵", "right": False},
                {"label": "🟢", "right": False},
            ],
        },
    },
    {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Tap the star to keep going!",
            "choices": [
                {"label": "⭐", "right": True},
                {"label": "🍌", "right": False},
                {"label": "🌱", "right": False},
            ],
        },
    },
    {
        "type": "type-this-word",
        "payload": {
            "prompt": "Type GO and press Send to unlock the question.",
            "target_display": "GO",
            "targets": ["go"],
            "hint_wrong": "Type the word GO and press Send.",
        },
    },
    {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Tap the rocket to launch the question!",
            "choices": [
                {"label": "🚀", "right": True},
                {"label": "🐢", "right": False},
                {"label": "🪨", "right": False},
            ],
        },
    },
    {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Tap the smiley to wake up Bytey!",
            "choices": [
                {"label": "😀", "right": True},
                {"label": "🥒", "right": False},
                {"label": "🧦", "right": False},
            ],
        },
    },
    {
        "type": "type-this-word",
        "payload": {
            "prompt": "Type YES and press Send to see the next question.",
            "target_display": "YES",
            "targets": ["yes"],
            "hint_wrong": "Type Y E S and press Send.",
        },
    },
    {
        "type": "click-the-thing",
        "payload": {
            "prompt": "Tap the heart to keep learning!",
            "choices": [
                {"label": "❤️", "right": True},
                {"label": "🥒", "right": False},
                {"label": "🌶️", "right": False},
            ],
        },
    },
]


# ----------------------------------------------------------------------------
# Per-lesson question count (3-8). Deterministic from lesson id so re-runs
# produce identical files.
# ----------------------------------------------------------------------------

def _question_count(lesson_id: int) -> int:
    return 4 + (lesson_id % 4)  # 4, 5, 6, 7 — middle of the 3-8 band


def _build_questions(lesson: dict[str, Any], seed: dict[str, Any]) -> list[dict[str, Any]]:
    n = _question_count(lesson["id"])
    questions: list[dict[str, Any]] = []

    # Q0 — keeps the original lesson.game as its gate; MCQ uses the lesson topic
    q0_interaction = lesson.get("game") or GATE_TEMPLATES[0]
    questions.append({
        "id": "q1",
        "interaction": q0_interaction,
        "variations": [
            _build_variation(FRAMES[v % len(FRAMES)], PARAPHRASES[v % len(PARAPHRASES)], seed, v, 0)
            for v in range(5)
        ],
    })

    # Q1..QN-1 — small rotating gates, MCQ frames cycle through the 5 frames
    for i in range(1, n):
        gate = GATE_TEMPLATES[i % len(GATE_TEMPLATES)]
        frame = FRAMES[i % len(FRAMES)]
        questions.append({
            "id": f"q{i + 1}",
            "interaction": gate,
            "variations": [
                _build_variation(frame, PARAPHRASES[v], seed, v, i)
                for v in range(5)
            ],
        })

    return questions


# ----------------------------------------------------------------------------
# Main entry
# ----------------------------------------------------------------------------

def expand_lesson(path: Path) -> bool:
    """Load lesson_NN.json, attach questions[], write back. Returns True on OK."""
    raw = path.read_text(encoding="utf-8")
    lesson: dict[str, Any] = json.loads(raw)
    lesson_id = int(lesson.get("id") or 0)
    seed = SEEDS.get(lesson_id)
    if seed is None:
        log.warning("no seed for lesson %d (%s); leaving alone", lesson_id, path.name)
        return False

    lesson["questions"] = _build_questions(lesson, seed)
    lesson["schema"] = "v2"  # marker so engine knows to use questions[]

    path.write_text(json.dumps(lesson, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("expanded %s — %d questions × %d variations",
             path.name, len(lesson["questions"]), len(lesson["questions"][0]["variations"]))
    return True


def main() -> int:
    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    if not files:
        log.error("no lesson files at %s", LESSONS_DIR)
        return 1
    ok = 0
    skipped = 0
    for f in files:
        try:
            if expand_lesson(f):
                ok += 1
            else:
                skipped += 1
        except Exception as exc:  # noqa: BLE001 — we want a single bad file not to nuke the run
            log.exception("FAIL %s: %s", f.name, exc)
            skipped += 1
    log.info("DONE — %d expanded, %d skipped", ok, skipped)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
