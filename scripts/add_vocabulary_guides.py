"""Add read-aloud vocabulary guides and simplify avoidably hard distractors."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = ROOT / "lessons"
MANIFEST = ROOT / "logs" / "vocabulary_audio_manifest.json"


GUIDES = {
    3: [("variable", "a named box in code that can hold a value")],
    6: [("artificial intelligence", "a computer system made to do jobs that usually need human thinking")],
    7: [("perceptron", "a tiny learning rule that sorts patterns into groups")],
    12: [("function", "a named set of code steps that you can use again")],
    28: [("function", "a named set of code steps that you can use again")],
    29: [("variable", "a named box in code that can hold a value")],
    44: [("iteration", "one round of building, testing, and improving")],
    46: [("iteration", "one round of building, testing, and improving")],
    50: [("iteration", "one round of building, testing, and improving")],
    51: [("iteration", "one round of building, testing, and improving")],
    52: [("iteration", "one round of building, testing, and improving")],
    53: [("iteration", "one round of building, testing, and improving")],
    54: [("iteration", "one round of building, testing, and improving")],
    55: [("iteration", "one round of building, testing, and improving")],
}

PLAIN_REWRITES = {
    "number-eating ducks": "ducks that munch numbers",
    "needs encouragement": "needs a kind cheer",
    "'abracadabra'": "'magic words'",
    "forever and unchangeable": "forever and can never change",
    "down-gravity": "normal gravity",
    "astrological sign": "star sign",
    "interpretive dance": "a dance routine",
    "feel any accomplishment": "feel proud of what they did",
    "they are paperweights": "they are heavy desk rocks",
    "international law": "a worldwide rule",
    "actuallyfinal": "really_final",
    "Gravity is unsubscribed": "Gravity was turned off",
    "gravity is unsubscribed": "gravity was turned off",
    "as compensation": "as a prize afterward",
    "that's old-fashioned": "that's out-of-date thinking",
    "dictionaries": "word books",
    "instructions": "directions",
    "improvements": "better changes",
    "explanations": "clear reasons",
    "descriptions": "details",
}


def _hash(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def main() -> None:
    audio: dict[str, str] = {}
    prompt_audio: dict[str, str] = {}
    changed_files = 0
    for path in sorted(LESSONS.glob("lesson_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        lesson_id = int(data["id"])
        changed = False
        if lesson_id in GUIDES:
            entries = []
            for word, meaning in GUIDES[lesson_id]:
                spoken = f"{word}. {meaning}."
                rel = f"assets/audio/o/{_hash(spoken)}.ogg"
                entries.append({"word": word, "meaning": meaning, "_audio": rel})
                audio[rel] = spoken
            if data.get("vocabulary") != entries:
                data["vocabulary"] = entries
                changed = True

        for question in data.get("questions", []):
            for variation in question.get("variations", []):
                old_prompt = str(variation.get("prompt", ""))
                new_prompt = old_prompt
                for source, replacement in PLAIN_REWRITES.items():
                    new_prompt = new_prompt.replace(source, replacement)
                if new_prompt != old_prompt:
                    variation["prompt"] = new_prompt
                    rel = str(variation.get("_audio", ""))
                    if rel:
                        prompt_audio[rel] = new_prompt
                    changed = True
                for option in variation.get("options", []):
                    old = str(option.get("text", ""))
                    new = old
                    for source, replacement in PLAIN_REWRITES.items():
                        new = new.replace(source, replacement)
                    if new == old:
                        continue
                    rel = f"assets/audio/o/{_hash(new)}.ogg"
                    option["text"] = new
                    option["_audio"] = rel
                    audio[rel] = new
                    changed = True

        if changed:
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            changed_files += 1

    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps({"prompts": prompt_audio, "options": audio}, indent=2,
                                   ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated {changed_files} lessons; {len(prompt_audio)} prompts and {len(audio)} spoken vocabulary items")


if __name__ == "__main__":
    main()
