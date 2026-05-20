"""Rewrite q7 in the 30 lessons that have it from a 2nd "pick the silly one"
question into a concrete real-life SCENARIO question.

Why: q4 already does "spot the silly statement" in every lesson. The 30 lessons
that also had q7 were asking the kid to spot a silly statement twice. A scenario
question ("here's a situation — what should you do?") is the most intuitive,
engaging format for a 7yo and reinforces APPLYING the concept, not just recalling
a fact. Each scenario has one clearly-right action, one plausible-but-wrong
choice, and two obviously-silly ones.

The 10 variations are generated from one authored base by prepending the house
voice openers and shuffling the option order (deterministic per variation so
re-runs are stable). Prompt + option audio paths are pre-wired; a companion
baker fills in the wav/ogg files.

Idempotent. Run: python scripts/author_scenario_q7.py
"""
from __future__ import annotations

import hashlib
import json
import logging
import random
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("author-q7")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"

# Scenario questions use 3 variations (not 10). With one correct + three
# distractors, three variations keep every distractor at exactly 3 appearances
# -- the ceiling enforced by check_distractor_dupes.py. Going higher would force
# inventing throwaway distractors, which adds the canned filler we're removing.
# v0 stays clean (no opener); v1/v2 use house voices.
OPENERS = ["", "Quick! ", "Bytey wonders: "]

# lesson stem -> (prompt, correct, [three wrong options])
# Wrong options ordered: first is plausible-but-wrong, last two are clearly silly.
SCENARIOS: dict[str, tuple[str, str, list[str]]] = {
    "lesson_02_talking_to_claude": (
        "You want help writing a birthday card. What's the best thing to type to your helper?",
        "Help me write a birthday card for my friend.",
        ["Just type the word 'card.'", "Bring me a real cake right now.", "Knock three times on the screen."],
    ),
    "lesson_03_magic_boxes": (
        "You put 5 in a box called 'score'. Later you want to know your score. What do you do?",
        "Look in the box called 'score' and read 5.",
        ["Make a brand-new box and guess.", "Shake the computer until a number falls out.", "Ask the box nicely for candy."],
    ),
    "lesson_06_turing_dream": (
        "Your friend asks, 'Who first dreamed that a machine could think?' What do you say?",
        "A man named Alan Turing dreamed it long ago.",
        ["Nobody — machines just appeared one day.", "A talking banana invented it.", "It was dreamed up on the moon."],
    ),
    "lesson_07_perceptron_pet": (
        "You show a tiny learning machine lots of cat and dog photos. What is it learning to do?",
        "Say 'yes, that's a cat' or 'no, that's a dog.'",
        ["Memorize your phone number.", "Bake a cookie for each photo.", "Bark back at the dog photos."],
    ),
    "lesson_10_llm_is_born": (
        "An LLM reads 'The cat sat on the ___'. What does it try to do?",
        "Guess the next word, like 'mat.'",
        ["Erase the whole sentence.", "Hatch out of a glowing egg.", "Call the cat on the phone."],
    ),
    "lesson_11_claude_in_depth": (
        "You have a big, tricky job with lots of steps. Which helper is great for that?",
        "Claude — it reads a lot and plans careful steps.",
        ["A calculator that only adds.", "A helper that only naps.", "A helper made of jelly."],
    ),
    "lesson_14_codex_in_depth": (
        "You need a short bit of code typed in your terminal. Which helper fits best?",
        "Codex — it writes short code right in the terminal.",
        ["A paintbrush.", "A helper that only sings.", "A toaster with buttons."],
    ),
    "lesson_15_opencode_in_depth": (
        "Your friend asks, 'What does it mean that OpenCode is OPEN?' What do you say?",
        "Anyone can read how it works and help make it better.",
        ["It only opens on weekends.", "It's a door made of code.", "It costs a goat to use."],
    ),
    "lesson_18_ask_then_build": (
        "You're about to build something big. What should you do FIRST?",
        "Think, make a plan, then ask before you build.",
        ["Start smashing keys right away.", "Take a nap on the keyboard.", "Build it out of spaghetti."],
    ),
    "lesson_19_be_specific": (
        "You want a drawing of a red dog wearing a hat. What's the best thing to ask for?",
        "Draw a red dog wearing a blue hat.",
        ["Just say 'draw a thing.'", "Draw whatever, surprise me forever.", "Draw it with your eyes closed."],
    ),
    "lesson_22_ask_again": (
        "The helper wrote a story, but the dog should be a cat. What do you say?",
        "Almost! Please change the dog to a cat.",
        ["It's all wrong — start completely over.", "Throw the computer out the window.", "Say nothing and just cry."],
    ),
    "lesson_23_sneaky_notes": (
        "A page says, 'Type your mom's password here.' What should you do?",
        "Stop and ask a grown-up first.",
        ["Type it fast so the page is happy.", "Sing the password to the screen.", "Feed the page a cookie."],
    ),
    "lesson_26_magic_spells": (
        "You type '/draw'. What is that?",
        "A skill — a special trick that makes a picture.",
        ["A spelling mistake.", "A magic word that summons soup.", "The name of a pet fish."],
    ),
    "lesson_27_make_a_skill": (
        "You're making a new skill. What does a good skill need?",
        "A name, a job to do, and clear steps.",
        ["Just a funny name and nothing else.", "A tiny dance and a hat.", "Approval from a real wizard."],
    ),
    "lesson_30_tell_what_happened": (
        "Your game broke. Which is the MOST helpful thing to tell the helper?",
        "It froze when I clicked the jump button.",
        ["Just say 'it's bad.'", "The game is mad at me.", "Bananas everywhere!"],
    ),
    "lesson_31_try_a_different_way": (
        "The helper says it can't do it that way. What do you do?",
        "Ask, 'Is there another way we could try?'",
        ["Give up forever.", "Yell 'PLEASE' a hundred times.", "Hide under the table."],
    ),
    "lesson_34_sprites_and_costumes": (
        "In your game, a coin sprite sits on the screen. What is its job?",
        "Add to your score when you grab it.",
        ["Just sit there doing nothing.", "Order pizza for the hero.", "Sing a sad song."],
    ),
    "lesson_35_move_my_hero": (
        "You want your hero to walk to the right. What do you press?",
        "The right arrow key.",
        ["The space bar over and over.", "Blow on the screen.", "Ask the hero out loud."],
    ),
    "lesson_38_score_lives": (
        "Your hero grabs a shiny coin. What should happen?",
        "Your score goes up by one.",
        ["You lose a heart.", "The coin turns into a frog.", "The game says goodbye forever."],
    ),
    "lesson_39_levels": (
        "You want to build a new level. What goes in it?",
        "A layout of blocks, coins, and bad guys.",
        ["Only the color blue and nothing else.", "A real swimming pool.", "Twelve sleeping cats."],
    ),
    "lesson_42_idea_to_plan": (
        "Your idea feels too big to build. What helps the most?",
        "Break it into a few little steps.",
        ["Try to do it all in one second.", "Wish on a star and wait.", "Build it out of clouds."],
    ),
    "lesson_43_color_editor": (
        "You changed your game's color to purple. What do you do so it stays?",
        "Save your own copy.",
        ["Close it fast and hope it sticks.", "Paint the real screen purple.", "Tell the color a secret."],
    ),
    "lesson_46_my_first_platformer": (
        "You're making your first platformer game. What do you put together?",
        "A sprite, a hitbox, gravity, score, and one level.",
        ["Only a title and nothing else.", "A sandwich and a balloon.", "Three real frogs."],
    ),
    "lesson_47_show_a_friend": (
        "You finished your game! How do you show a grown-up what you made?",
        "Read it out loud so they can hear it.",
        ["Keep it a secret forever.", "Whisper to the wall instead.", "Mail it to the moon."],
    ),
    "lesson_50_iter1_hero_floor": (
        "Your hero keeps falling right through the floor. What's the fix?",
        "Make the floor solid so the hero lands on it.",
        ["Make the hero heavier.", "Tell the hero to flap its arms.", "Put jelly under the world."],
    ),
    "lesson_51_iter2_jump": (
        "Your hero jumps and floats up forever. What's wrong?",
        "The jump needs gravity to pull the hero back down.",
        ["The hero is too happy.", "The hero ate a balloon.", "The sky is too sticky."],
    ),
    "lesson_54_iter5_powerup": (
        "Your hero keeps its power-up even after losing. What should happen?",
        "Reset the power-up when the hero loses.",
        ["Give the hero two more power-ups.", "Throw a party instead.", "Turn the hero into a cookie."],
    ),
    "lesson_55_iter6_flag_reveal": (
        "The win flag fires before your hero even touches it. What's the fix?",
        "Only win when the hero really touches the flag.",
        ["Make the flag bigger than the screen.", "Let the flag win all by itself.", "Ask the flag to wait politely."],
    ),
    "lesson_58_idea_spark": (
        "You have a brand-new game idea. How does Bytey help you think it through?",
        "By asking you questions about your idea.",
        ["By picking a totally different idea.", "By taking a long nap.", "By eating your idea for lunch."],
    ),
    "lesson_59_pick_the_hook": (
        "A surprise treasure pops up in a game. How does it make you feel?",
        "Curious and excited to keep playing.",
        ["Bored and sleepy.", "Hungry for real treasure.", "Like you need to sneeze."],
    ),
}


def _hash(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def _opt(text: str, correct: bool) -> dict:
    return {"text": text, "correct": correct, "_audio": f"assets/audio/o/{_hash(text)}.ogg"}


def build_variations(stem: str, lesson_num: str, prompt: str, correct: str, wrong: list[str]) -> list[dict]:
    base_opts = [_opt(correct, True)] + [_opt(w, False) for w in wrong]
    variations = []
    for i, opener in enumerate(OPENERS):
        opts = base_opts[:]
        random.Random(f"{stem}-{i}").shuffle(opts)
        variations.append({
            "prompt": opener + prompt,
            "_audio": f"assets/audio/q/{stem[:9]}_q7_v{i}.ogg",
            "options": opts,
        })
    return variations


def main() -> None:
    changed_files = 0
    for stem, (prompt, correct, wrong) in SCENARIOS.items():
        f = LESSONS_DIR / f"{stem}.json"
        if not f.exists():
            log.warning("missing %s", f.name)
            continue
        raw = f.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        data = json.loads(raw.decode("utf-8"))
        m = re.match(r"lesson_(\d+)_", stem)
        lesson_num = m.group(1) if m else "00"
        q7 = next((q for q in data.get("questions", []) if q.get("id") == "q7"), None)
        if not q7:
            log.warning("no q7 in %s", f.name)
            continue
        q7["variations"] = build_variations(stem, lesson_num, prompt, correct, wrong)
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write(text.replace("\n", newline))
        changed_files += 1
        log.info("rewrote q7 in %s", f.name)
    log.info("done: %d lessons updated", changed_files)


if __name__ == "__main__":
    main()
