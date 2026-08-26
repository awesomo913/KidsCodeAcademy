"""Regression tests for the native persistence and project bridge."""
from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# Bridge tests do not create a GUI; keep them runnable in lint-only Python
# environments where pywebview is intentionally absent.
sys.modules.setdefault("webview", types.ModuleType("webview"))
import app


class BridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="kca_backend_")
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(app, "_appdata_root", return_value=self.root)
        self.root_patch.start()
        self.bridge = app.JSBridge()

    def tearDown(self) -> None:
        self.root_patch.stop()
        self.temp.cleanup()

    def test_state_accepts_only_json_objects_and_preserves_good_data(self) -> None:
        good = json.dumps({"kca.progress.v1": {"completed": {"lesson_01": "today"}}})
        self.assertTrue(self.bridge.save_state(good)["ok"])
        state_file = self.root / "state.json"
        original = state_file.read_text(encoding="utf-8")
        for bad in ("not json", "[]", '"text"'):
            self.assertFalse(self.bridge.save_state(bad)["ok"])
            self.assertEqual(state_file.read_text(encoding="utf-8"), original)

    def test_project_names_types_and_sizes_are_bounded(self) -> None:
        self.assertFalse(self.bridge.save_kid_project("../oops.json", "{}")["ok"])
        self.assertFalse(self.bridge.save_kid_project("oops.exe", "{}")["ok"])
        self.assertFalse(self.bridge.save_kid_project("ok.json", b"no")["ok"])
        self.assertFalse(self.bridge.save_kid_project("huge.json", "x" * (2 * 1024 * 1024 + 1))["ok"])
        self.assertTrue(self.bridge.save_kid_project("my_game.json", '{"game_name":"My Game"}')["ok"])

    def test_project_listing_skips_valid_json_that_is_not_an_object(self) -> None:
        user = app.get_user_data_dir()
        (user / "array.json").write_text("[]", encoding="utf-8")
        (user / "string.json").write_text('"hello"', encoding="utf-8")
        (user / "good.json").write_text('{"game_name":"Good","kind":"capstone"}', encoding="utf-8")
        items = self.bridge.list_kid_projects()
        self.assertEqual([item["name"] for item in items], ["Good"])

    def test_generated_project_view_escapes_saved_text(self) -> None:
        rendered = app._render_project_view({"note": "<script>alert(1)</script>"}, "<bad>")
        self.assertNotIn("<script>alert(1)</script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;bad&gt;", rendered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
