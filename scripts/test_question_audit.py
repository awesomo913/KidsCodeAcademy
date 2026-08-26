"""Regression tests for curriculum and Word Power quality gates."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import audit_question_quality as audit_module


class VocabularyAuditTests(unittest.TestCase):
    def _audit(self, meaning: str, typing_payload: dict | None = None) -> dict:
        with tempfile.TemporaryDirectory(prefix="kca_vocab_audit_") as temp:
            root = Path(temp)
            lessons = root / "lessons"
            audio = root / "assets" / "audio" / "o"
            lessons.mkdir(parents=True)
            audio.mkdir(parents=True)
            (audio / "test.ogg").write_bytes(b"test")
            lesson = {
                "id": 1,
                "vocabulary": [{
                    "word": "variable",
                    "meaning": meaning,
                    "_audio": "assets/audio/o/test.ogg",
                }],
                "questions": [{
                    "id": "q1",
                    "interaction": {
                        "type": "type-this-word",
                        "payload": typing_payload if typing_payload is not None else {
                            "prompt": "Type the word CODE!",
                            "target_display": "CODE",
                            "targets": ["code"],
                            "hint_wrong": "Type the word CODE.",
                        },
                    },
                    "variations": [{
                        "prompt": "Which description of a variable is correct?",
                        "_audio": "assets/audio/o/test.ogg",
                        "options": [
                            {"text": "A named box in code", "correct": True, "_audio": "assets/audio/o/test.ogg"},
                            {"text": "A button on the screen", "correct": False, "_audio": "assets/audio/o/test.ogg"},
                            {"text": "A picture saved online", "correct": False, "_audio": "assets/audio/o/test.ogg"},
                            {"text": "A sound from a speaker", "correct": False, "_audio": "assets/audio/o/test.ogg"},
                        ],
                    }],
                }],
            }
            (lessons / "lesson_01_test.json").write_text(
                json.dumps(lesson), encoding="utf-8"
            )
            with (
                patch.object(audit_module, "ROOT", root),
                patch.object(audit_module, "LESSONS_DIR", lessons),
            ):
                return audit_module.audit()

    def test_plain_definition_allows_taught_technical_word(self) -> None:
        result = self._audit("a named box in code that can hold a value")
        self.assertEqual([], result["findings"]["weak_vocabulary"])
        self.assertEqual([], result["findings"]["hard_word"])
        self.assertEqual([], result["findings"]["missing_audio"])

    def test_missing_definition_cannot_hide_jargon(self) -> None:
        result = self._audit("")
        self.assertEqual(1, len(result["findings"]["weak_vocabulary"]))
        self.assertEqual(1, len(result["findings"]["hard_word"]))

    def test_definition_cannot_use_unexplained_jargon(self) -> None:
        result = self._audit("a named box that uses polymorphism in code")
        self.assertEqual(1, len(result["findings"]["weak_vocabulary"]))
        self.assertEqual(1, len(result["findings"]["hard_word"]))

    def test_typing_activity_requires_visible_target_and_accepted_answer(self) -> None:
        result = self._audit(
            "a named box in code that can hold a value",
            {"prompt": "Type this word!", "word": "CODE"},
        )
        self.assertEqual(1, len(result["findings"]["invalid_interaction"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
