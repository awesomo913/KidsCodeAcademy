"""Remove synthetic quiz filler and restore natural answer choices.

Older diversification passes made repeated text look different by adding
phrases such as ``Rumor:``, ``I think``, or ``(no way)``.  They also prefixed
otherwise clear prompts with ``Quick!`` and ``Wait wait wait``.  Those edits
increase string counts without improving the lesson.

This migration keeps the authored facts and scenarios, removes the wrappers,
normalizes worn-out quiz frames, and guarantees at least one believable
misconception whenever a truth question would otherwise have three joke
answers.  Changed audio is emitted as a targeted Piper manifest.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from copy import deepcopy
from pathlib import Path

from refine_flagged_questions import Q5_PROMPTS

ROOT = Path(__file__).resolve().parent.parent
LESSONS = ROOT / "lessons"
MANIFEST = ROOT / "logs" / "content_polish_audio_manifest.json"

PROMPT_PREFIX = re.compile(
    r"^(?:Quick!|Hey friend\s*[—-]|Bytey wonders:|Tell me\s*[—-]|"
    r"Wait wait wait\s*[—-]|Pop quiz!|Listen up\s*[—-]|Think about this:|"
    r"Got a quick one:|Brain time:)\s*",
    re.IGNORECASE,
)

OPTION_PREFIXES = (
    "I think ", "Actually, ", "Maybe ", "Maybe: ", "Some say ",
    "Word is, ", "Bytey heard ", "Rumor: ", "Story goes — ",
    "I bet ", "Pretty sure ",
)
OPTION_SUFFIXES = (
    " (or so they say)", " — for real?", " (true story?)", "... right?",
    " (silly idea)", " (no way)", " (myth)", " (false alarm)",
)
OPTION_REWRITES = {
    "Code? Maybe": "Write some code for me, maybe.",
    "Code? Maybe?": "Write some code for me, maybe.",
    "Tax form": "A long tax form full of tiny boxes.",
    "Tax form.": "A long tax form full of tiny boxes.",
}
CONTEXT_OPTION_REWRITES = {
    (3, "q3", "Both 5 and 10 stacked like pancakes"):
        "The box name does not matter, so random letters are fine.",
    (3, "q5", "Both 5 and 10 stacked like pancakes"):
        "A box remembers every old value at the same time.",
    (2, "q5", "There is a butterfly in the keyboard"):
        "Claude understands exactly what you want from one vague word.",
    (3, "q6", "Nothing -- variables empty themselves"):
        "Reading a variable empties it.",
    (3, "q8", "Nothing -- variables empty themselves"):
        "Variables erase themselves after each step.",
    (3, "q6", "Just '30' because they got added"):
        "Changing a value adds the old and new numbers.",
    (3, "q8", "Just '30' because they got added"):
        "A box keeps its first number forever.",
    (3, "q7", "Shake the computer until a number falls out"):
        "Guess the value without checking the box.",
    (3, "q7", "Make a brand-new box and guess"):
        "Create another box instead of reading the first one.",
    (12, "q5", "Cursor only works inside a pumpkin"):
        "Cursor can edit any file without you showing the project.",
    (12, "q5", "Cursor uses extra exclamation marks"):
        "More exclamation marks help Cursor understand code.",
    (12, "q5", "Cursor has way prettier buttons"):
        "Prettier buttons make Cursor understand code better.",
    (35, "q6", "Pressing keys causes mild thunder"):
        "Pressing a key moves the hero even without movement code.",
    (35, "q7", "The space bar over and over"):
        "Press the space bar repeatedly instead of changing the code.",
    (35, "q6", "To wear out the keyboard faster"):
        "Larger movement steps always make motion smoother.",
    (35, "q7", "Ask the hero out loud"):
        "Ask the hero to move without adding an input rule.",
    (35, "q6", "Frames demand attention"):
        "The number of frames does not change how motion looks.",
}
CONTEXT_VARIATION_REWRITES = {
    (3, "q3", 5): "The box name does not matter, so random letters are fine.",
    (3, "q5", 5): "A box remembers every old value at the same time.",
    (16, "q5", 5): "Ollama sends every question to the internet first.",
    (16, "q1", 5): "Ollama needs a working internet connection.",
}
CONTEXT_QUESTION_REWRITES = {
    (16, "q2"): "Wait until the internet comes back before chatting.",
}

# Broad enough to recognize authored joke answers without banning comedy from
# the curriculum.  It is used only to ensure a truth question also includes a
# believable misconception that requires thought.
COMEDY = re.compile(
    r"\b(allergic|broccoli|sandwich|squirrel|dragon|giggle|couch|banana|"
    r"pancakes?|butterfl|lamp|homework|sneaker|cookie|farm|oil|puppy|bees?|"
    r"fridge|lasagna|tuesdays?|storm|carrots?|dreams?|cry|cheese|moth|"
    r"breakfast|hat|goose|pizza|sock|sneeze|moon|lullaby|wizard|onion|"
    r"slipper|jelly|cloud|whistle|bark|egg|dance|spin|sing|tickle|burp|"
    r"unicorn|spaghetti|frog|candy|smell|melt|feelings?|lemon|shoe|teacup|"
    r"leaf pile|bow before|parade|wifi|tiny chefs?|weather report|curfew|"
    r"soprano|cello|goldfish|jealous|shelf space|jars?|sacred|odd hats?|"
    r"sniff|snacks?|riddles?|butterfl|loud enough|vowels?|yelling|tiny dog|"
    r"paid|shy compliments?|pictures? of your foot|mail your question|wall|"
    r"invisible ink|computer needs a nap|slap the laptop|peanut|hot air balloon|"
    r"tiny mice|one tiny book|gummy worms?|sip of water|magic stones?|pebbles|"
    r"using its tail|spinning in circles|logs? out forever|bank closings?|holidays?|"
    r"24 hours?|grocery list|in pencil|turns purple|only on weekdays|at midnight|"
    r"taxes|sad and damp|rot if|scare people|approved by a committee|"
    r"grandparent|afraid of them|required to make a sequel|disappears?|"
    r"stacked on top|butterfl|smells? the code|loaf of bread|refuse to load|"
    r"written sideways|earns? you .*stars?|bold is best|gets? shorter|"
    r"invisible until .* says hi|x turns into y|song without lyrics|yell .?math|"
    r"local models? can fly|helper cries|saturdays?|singing chef|sings? every change|"
    r"inhaling crayons|because shy|tiny hats?|blob files?|gets? dizzy|sit there doing nothing|"
    r"secret forever|helps? no one|grows? new keys|never work,? ever|metal trees|"
    r"mushy notes?|only emoji|boring on purpose|does something fun|bigger ideas? are always|"
    r"long stories with chapters|last part you build|flying horse|train on mars|"
    r"slowest helper|llama .* closet|frowns? at parents|invisible coins|"
    r"signatures? and a stamp|write a poem instead)\b",
    re.IGNORECASE,
)


def _hash(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def _reuse_key(text: str) -> str:
    return text.strip().rstrip(".!?").casefold()


def _capitalize(text: str) -> str:
    if not text or text[0] in "'`\"":
        return text
    return text[0].upper() + text[1:]


def clean_option(text: str) -> str:
    value = text.strip()
    changed = True
    while changed:
        changed = False
        for prefix in OPTION_PREFIXES:
            if value.startswith(prefix):
                value = _capitalize(value[len(prefix):].lstrip())
                changed = True
                break
        for suffix in OPTION_SUFFIXES:
            if value.endswith(suffix):
                value = value[:-len(suffix)].rstrip()
                changed = True
                break
    return OPTION_REWRITES.get(value, value)


def clean_prompt(text: str, *, lesson_id: int, qid: str, vidx: int, concept: str) -> str:
    value = text.strip()
    while True:
        cleaned = PROMPT_PREFIX.sub("", value)
        if cleaned == value:
            break
        value = cleaned.strip()

    # The old Q1-v0 migration used eight emoji-heavy pep-talks.  Q1-v0 always
    # asks for a true fact, so replace the pep talk with the actual task.
    # Q5 has a hand-written, lesson-specific check in its authored slot;
    # other variations keep their own question types and matching answers.
    if qid == "q5" and vidx == 7 and lesson_id in Q5_PROMPTS:
        value = Q5_PROMPTS[lesson_id]

    replacements = (
        (r"^Which one is TRUE about (.+)\?$", r"Which fact about \1 is correct?"),
        (r"^One of these is silly! Pick the WRONG one about (.+)\.$", r"Which statement about \1 is incorrect?"),
        (r"^One of these about (.+) is silly\. Pick the silly one!$", r"Which statement about \1 does not belong?"),
        (r"^Bytey claims something about (.+)\. Pick the SILLIEST claim\.$", r"Which claim about \1 is incorrect?"),
        (r"^Which rule about (.+) is a GOOD rule\?$", r"Which rule works well for \1?"),
        (r"^What WOULD really happen with (.+)\?$", r"What would really happen with \1?"),
        (r"^How would you tell your grandma about (.+)\? Pick the BEST way\.$", r"How would you explain \1 to a family member?"),
        (r"^Three of these are jokes\. Pick the one that's actually true about (.+)\.$", r"Which statement about \1 is correct?"),
        (r"^A robot is learning about (.+)\. Which thing it says is right\?$", r"A robot is learning about \1. Which statement is correct?"),
    )
    for pattern, repl in replacements:
        value = re.sub(pattern, repl, value, flags=re.IGNORECASE)

    value = re.sub(
        r"^Pick the most Turing-y idea:$",
        "Which idea best matches Alan Turing's dream?",
        value,
        flags=re.IGNORECASE,
    )
    # "Directions" is the familiar elementary-school word for this idea.
    value = re.sub(r"\binstructions\b", "directions", value, flags=re.IGNORECASE)

    # Emphasis belongs in the spoken meaning, not in random capital letters.
    value = re.sub(r"\b(FIRST|ADD|BEST|GOOD|WOULD|TRUE|WRONG|MOST)\b", lambda m: m.group(1).lower(), value)
    return value


def main() -> int:
    previous = {"prompts": {}, "options": {}}
    if MANIFEST.exists():
        try:
            loaded = json.loads(MANIFEST.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                previous = loaded
        except (OSError, json.JSONDecodeError):
            pass
    # Merging makes the migration safe to rerun while a large audio batch is
    # still pending. The baker removes this manifest after a successful run.
    prompt_audio: dict[str, str] = dict(previous.get("prompts") or {})
    # Rebuild the option manifest from the final answer sets. This drops paths
    # from an interrupted/obsolete migration while prompt paths remain merged.
    option_audio: dict[str, str] = {}
    changed_files = changed_prompts = changed_options = misconception_swaps = 0

    for path in sorted(LESSONS.glob("lesson_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        original = json.loads(subprocess.check_output(
            ["git", "show", f"HEAD:lessons/{path.name}"], cwd=ROOT
        ).decode("utf-8"))
        lesson_id = int(data["id"])
        concept = str(data.get("title") or "this lesson").strip().rstrip(".!?").lower()

        # Collect believable wrong answers authored for this lesson.  Never
        # borrow a statement that is marked correct anywhere else.
        correct_texts = {
            clean_option(str(o.get("text") or ""))
            for q in original.get("questions", [])
            if not str(q.get("id", "")).startswith("math")
            for v in q.get("variations", [])
            for o in v.get("options", []) if o.get("correct")
        }
        believable_pool: list[str] = []
        believable_keys: set[str] = set()
        replacement_questions: dict[str, set[str]] = {}
        question_order = {str(q.get("id", "")): index for index, q in enumerate(original.get("questions", []))}
        for q in original.get("questions", []):
            if str(q.get("id", "")).startswith("math"):
                continue
            for v in q.get("variations", []):
                for option in v.get("options", []):
                    if option.get("correct"):
                        continue
                    candidate = clean_option(str(option.get("text") or ""))
                    if candidate:
                        replacement_questions.setdefault(_reuse_key(candidate), set()).add(str(q.get("id", "")))
                    candidate_key = _reuse_key(candidate)
                    if (candidate and len(re.findall(r"[A-Za-z0-9]+", candidate)) > 2
                            and candidate not in correct_texts and not COMEDY.search(candidate)
                            and candidate_key not in believable_keys):
                        believable_pool.append(candidate)
                        believable_keys.add(candidate_key)

        changed = False
        for question in data.get("questions", []):
            qid = str(question.get("id", ""))
            if qid.startswith("math"):
                continue
            variations = question.get("variations", [])
            if not variations:
                continue
            original_question = next((q for q in original.get("questions", []) if str(q.get("id", "")) == qid), None)
            if not original_question or len(original_question.get("variations", [])) != len(variations):
                raise ValueError(f"{path.name} {qid}: cannot align with the baseline question")

            cleaned_prompts = []
            for index, baseline_variation in enumerate(original_question.get("variations", [])):
                # Q1-v0's old emoji pep talk had no useful topic. Q1-v1 is the
                # same truth-check format with a natural, authored concept.
                source_prompt = (original_question["variations"][1].get("prompt")
                                 if qid == "q1" and index == 0 and len(variations) > 1
                                 else baseline_variation.get("prompt"))
                cleaned_prompts.append(clean_prompt(
                    str(source_prompt or ""), lesson_id=lesson_id, qid=qid,
                    vidx=(1 if qid == "q1" and index == 0 else index), concept=concept,
                ))
            # Candidate answers may be shared only among replays that ask the
            # same cleaned question. This preserves the difference between
            # "pick the true fact" and "pick the incorrect statement."
            wrong_by_prompt: dict[str, list[str]] = {}
            for index, baseline_variation in enumerate(original_question.get("variations", [])):
                pool = wrong_by_prompt.setdefault(cleaned_prompts[index], [])
                for option in baseline_variation.get("options", []):
                    if option.get("correct"):
                        continue
                    candidate = clean_option(str(option.get("text") or ""))
                    if len(re.findall(r"[A-Za-z0-9]+", candidate)) > 2 and candidate not in pool:
                        pool.append(candidate)

            for vidx, variation in enumerate(variations):
                old_prompt = str(variation.get("prompt") or "")
                new_prompt = cleaned_prompts[vidx]
                if new_prompt != old_prompt:
                    variation["prompt"] = new_prompt
                    rel = str(variation.get("_audio") or f"assets/audio/q/lesson_{lesson_id:02d}_{qid}_v{vidx}.ogg")
                    variation["_audio"] = rel
                    prompt_audio[rel] = new_prompt
                    changed_prompts += 1
                    changed = True

                old_options = variation.get("options", [])
                baseline_options = original_question["variations"][vidx].get("options", [])
                desired = deepcopy(baseline_options)
                for option in desired:
                    option["text"] = clean_option(str(option.get("text") or ""))

                present: set[str] = set()
                for option in desired:
                    text = str(option.get("text") or "")
                    text_key = _reuse_key(text)
                    is_bare = len(re.findall(r"[A-Za-z0-9]+", text)) <= 2
                    used_in = replacement_questions.get(text_key, set())
                    keep_in = sorted(used_in, key=lambda item: question_order.get(item, 999))[:3]
                    overused_here = len(used_in) > 3 and qid not in keep_in
                    if not option.get("correct") and (text_key in present or is_bare or overused_here):
                        visible_problem = text_key in present or is_bare
                        desired_keys = {_reuse_key(str(o.get("text") or "")) for o in desired}
                        replacement = next((candidate for candidate in wrong_by_prompt.get(cleaned_prompts[vidx], [])
                                            if _reuse_key(candidate) not in present and
                                            _reuse_key(candidate) not in desired_keys and
                                            (visible_problem or
                                             len(replacement_questions.get(_reuse_key(candidate), set())) < 3)), "")
                        if replacement:
                            option["text"] = replacement
                            text = replacement
                            text_key = _reuse_key(text)
                            replacement_questions.setdefault(text_key, set()).add(qid)
                    present.add(text_key)
                for option in desired:
                    text = str(option.get("text") or "")
                    text = CONTEXT_OPTION_REWRITES.get((lesson_id, qid, text.rstrip(".!?")), text)
                    option["text"] = text
                contextual = (CONTEXT_VARIATION_REWRITES.get((lesson_id, qid, vidx))
                              or CONTEXT_QUESTION_REWRITES.get((lesson_id, qid)))
                if contextual:
                    target = next((option for option in reversed(desired) if not option.get("correct")), None)
                    if target:
                        target["text"] = contextual
                for option in desired:
                    text = str(option.get("text") or "")
                    rel = f"assets/audio/o/{_hash(text)}.ogg"
                    option["_audio"] = rel
                    option_audio[rel] = text

                if old_options != desired:
                    changed_options += sum(
                        1 for index, option in enumerate(desired)
                        if index >= len(old_options) or old_options[index] != option
                    )
                    variation["options"] = desired
                    changed = True

                opts = variation.get("options", [])
                correct = next((str(o.get("text") or "") for o in opts if o.get("correct")), "")
                wrong = [o for o in opts if not o.get("correct")]
                if correct and not COMEDY.search(correct) and wrong and all(COMEDY.search(str(o.get("text") or "")) for o in wrong):
                    present = {str(o.get("text") or "") for o in opts}
                    candidates = [x for x in believable_pool if x not in present]
                    replacement = min(
                        candidates,
                        key=lambda x: (len(replacement_questions.get(_reuse_key(x), set())), believable_pool.index(x)),
                        default="",
                    )
                    if replacement:
                        target = wrong[-1]
                        target["text"] = replacement
                        rel = f"assets/audio/o/{_hash(replacement)}.ogg"
                        target["_audio"] = rel
                        option_audio[rel] = replacement
                        replacement_questions.setdefault(_reuse_key(replacement), set()).add(qid)
                        misconception_swaps += 1
                        changed = True

                # Misconception balancing may choose a broadly reused lesson
                # option. Reapply the small contextual edits last so their
                # wording cannot be overwritten by that balancing pass.
                for option in opts:
                    before = str(option.get("text") or "")
                    after = CONTEXT_OPTION_REWRITES.get((lesson_id, qid, before.rstrip(".!?")), before)
                    if after != before:
                        option["text"] = after
                        rel = f"assets/audio/o/{_hash(after)}.ogg"
                        option["_audio"] = rel
                        option_audio[rel] = after
                        changed = True
                contextual = (CONTEXT_VARIATION_REWRITES.get((lesson_id, qid, vidx))
                              or CONTEXT_QUESTION_REWRITES.get((lesson_id, qid)))
                if contextual:
                    target = next((option for option in reversed(opts) if not option.get("correct")), None)
                    if target and target.get("text") != contextual:
                        target["text"] = contextual
                        rel = f"assets/audio/o/{_hash(contextual)}.ogg"
                        target["_audio"] = rel
                        option_audio[rel] = contextual
                        changed = True

        if changed:
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            changed_files += 1

    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps({"prompts": prompt_audio, "options": option_audio}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"polished {changed_files} lesson files")
    print(f"changed prompts={changed_prompts}, options={changed_options}, believable swaps={misconception_swaps}")
    print(f"audio manifest: prompts={len(prompt_audio)}, unique options={len(option_audio)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
