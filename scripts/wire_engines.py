"""Wire v0.3.1 mini-game engines into the relevant lesson JSONs.

- Chapter 2 (lessons 5-10) -> history-scene with comprehension check
- Lessons 19, 20, 22 -> prompt-grader with rubric
- Lessons 35, 36, 37, 46 -> sprite-mover with level + options
- Lessons 39, 44 -> level-painter
"""
from __future__ import annotations

import json
import logging
import pathlib

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("wire")

ROOT = pathlib.Path(__file__).resolve().parent.parent
LESSONS = ROOT / "lessons"


def patch(fn: str, new_game: dict) -> None:
    p = LESSONS / fn
    if not p.is_file():
        log.warning("missing %s", fn)
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    data["game"] = new_game
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log.info("wired %s -> %s", fn, new_game["type"])


# === Chapter 2 history scenes ====================
HISTORY: dict[str, tuple[str, dict]] = {
    "lesson_05_math_made_thinking.json": ("math", {
        "prompt": "In the scene, what did 2 + 3 become?",
        "choices": [
            {"label": "5 →", "right": True},
            {"label": "7", "right": False},
            {"label": "A picture", "right": False},
            {"label": "0", "right": False},
        ],
    }),
    "lesson_06_turing_dream.json": ("turing", {
        "prompt": "What did the head do across the tape?",
        "choices": [
            {"label": "Read each square one at a time", "right": True},
            {"label": "Threw the tape away", "right": False},
            {"label": "Sang a song", "right": False},
            {"label": "Erased everything", "right": False},
        ],
    }),
    "lesson_07_perceptron_pet.json": ("perceptron", {
        "prompt": "What did the brain cell answer at the end?",
        "choices": [
            {"label": "YES", "right": True},
            {"label": "MAYBE", "right": False},
            {"label": "PIZZA", "right": False},
            {"label": "Nothing", "right": False},
        ],
    }),
    "lesson_08_back_and_forth_learning.json": ("training", {
        "prompt": "Where did the guess move toward?",
        "choices": [
            {"label": "The green target", "right": True},
            {"label": "The clouds", "right": False},
            {"label": "Off the screen", "right": False},
            {"label": "The ground", "right": False},
        ],
    }),
    "lesson_09_word_attention.json": ("attention", {
        "prompt": "The arrow showed which word looks at which?",
        "choices": [
            {"label": "She → Mom", "right": True},
            {"label": "smiles → She", "right": False},
            {"label": "No words look at each other", "right": False},
            {"label": "Mom → smiles", "right": False},
        ],
    }),
    "lesson_10_llm_is_born.json": ("llm", {
        "prompt": "What happened to the words during the scene?",
        "choices": [
            {"label": "They drifted into a big brain", "right": True},
            {"label": "They disappeared off-screen", "right": False},
            {"label": "They turned into numbers", "right": False},
            {"label": "They got bigger and bigger", "right": False},
        ],
    }),
}
for fn, (scene_id, check) in HISTORY.items():
    patch(fn, {
        "type": "history-scene",
        "payload": {
            "prompt": "Watch the scene, then answer the question!",
            "scene": {"id": scene_id, "check": check},
        },
    })

# === Chapter 4 prompt-grader =====================
PROMPT_GRADERS: dict[str, dict] = {
    "lesson_19_be_specific.json": {
        "prompt": "Type a clear, specific prompt for a robot:",
        "goal": "Use details like size, color, and special parts.",
        "rubric": {
            "minWords": 6,
            "mustInclude": ["small", "red"],
            "mustHaveExample": False,
            "idealLength": [6, 30],
            "passingStars": 4,
        },
    },
    "lesson_20_show_dont_tell.json": {
        "prompt": "Type a prompt that SHOWS with an example:",
        "goal": "Use the word 'like' or a colon (:) so the robot can copy the shape.",
        "rubric": {
            "minWords": 5,
            "mustInclude": [],
            "mustHaveExample": True,
            "idealLength": [5, 35],
            "passingStars": 4,
        },
    },
    "lesson_22_ask_again.json": {
        "prompt": "The robot drew a HUGE star. Reply with a clear fix:",
        "goal": "Tell the robot WHAT to change (e.g. make it small).",
        "rubric": {
            "minWords": 4,
            "mustInclude": ["small"],
            "mustHaveExample": False,
            "idealLength": [4, 25],
            "passingStars": 4,
        },
    },
}
for fn, payload in PROMPT_GRADERS.items():
    patch(fn, {"type": "prompt-grader", "payload": payload})

# === Chapter 7 sprite-mover + Chapter 8 capstone =
SPRITE: dict[str, dict] = {
    "lesson_35_move_my_hero.json": {
        "prompt": "Use arrow keys (or A/D) to walk. Up/W/Space to jump. Reach the green flag!",
        "levelId": "starter",
        "options": {"showHitboxToggle": False},
    },
    "lesson_36_hitboxes.json": {
        "prompt": "Click 'Hitboxes' to see the bump boxes! Then reach the flag.",
        "levelId": "hitbox_demo",
        "options": {"showHitboxToggle": True, "debugDefault": True},
    },
    "lesson_37_gravity.json": {
        "prompt": "Try the gravity slider. Higher = harder to jump. Reach the flag!",
        "levelId": "jump_practice",
        "options": {"showHitboxToggle": True, "gravitySlider": True},
    },
    "lesson_46_my_first_platformer.json": {
        "prompt": "Bring it all together. Avoid bad guys, grab coins, reach the flag!",
        "levelId": "enemy_demo",
        "options": {"showHitboxToggle": True},
    },
}
for fn, payload in SPRITE.items():
    patch(fn, {"type": "sprite-mover", "payload": payload})

# === level-painter ===============================
PAINTER: dict[str, dict] = {
    "lesson_39_levels.json": {
        "prompt": "Paint your own level! Pick tiles, click to place. Save to finish.",
    },
    "lesson_44_level_editor.json": {
        "prompt": "Capstone! Build a real level with 1 hero, coins, a flag — then save it.",
    },
}
for fn, payload in PAINTER.items():
    patch(fn, {"type": "level-painter", "payload": payload})

log.info("DONE")
