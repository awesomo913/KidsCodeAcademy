"""Sandbox JSON validator — runs at build time before PyInstaller.

Catches typos in `sandbox_ai/<helper>/lesson_NN.json` files BEFORE they ship.
Currently the runtime falls back to a generic "Hmm, try something else!" string
when a sandbox file is malformed, masking authoring bugs. This script makes the
build fail loud instead.

Validates:
  * required top-level keys: helper, lesson_id, fallback, matches
  * helper matches /^[a-z]+$/ AND matches the parent dir name
  * each match entry has keywords[] (>=1) and reply_lines[] (>=1)
  * side_effect.action is in the whitelist of 9 names
  * fallback string mentions at least one keyword from matches[]
    (so the kid is never dead-ended)

Usage:
  python scripts/sandbox_lint.py            # exits 0 if clean, 1 otherwise
  python scripts/sandbox_lint.py --quiet    # only print failures
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SANDBOX_DIR = ROOT / "sandbox_ai"

HELPER_RE = re.compile(r"^[a-z]+$")
ALLOWED_ACTIONS = {
    "draw_svg",
    "show_text",
    "show_code_diff",
    "show_picture",
    "show_terminal",
    "show_thinking",
    "show_inline_complete",
    "open_local_badge",
    "attach_image_chip",
}
ALLOWED_PICTURE_IDS = {"kitten", "dinosaur", "solar_system", "robot", "star_field", "cat_in_box"}


class LintError(Exception):
    pass


def _err(path: Path, msg: str) -> str:
    return f"FAIL {path.relative_to(ROOT)}: {msg}"


def lint_file(path: Path) -> list[str]:
    """Return a list of error strings (empty list = clean)."""
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [_err(path, f"invalid JSON ({exc})")]

    if not isinstance(data, dict):
        return [_err(path, "top-level must be an object")]

    # Required keys
    for k in ("helper", "lesson_id", "fallback", "matches"):
        if k not in data:
            errors.append(_err(path, f"missing required key '{k}'"))

    # helper checks
    helper = data.get("helper", "")
    if not isinstance(helper, str) or not HELPER_RE.match(helper):
        errors.append(_err(path, f"helper must match /^[a-z]+$/, got {helper!r}"))
    parent_name = path.parent.name
    if helper and helper != parent_name:
        errors.append(_err(path, f"helper {helper!r} does not match parent dir {parent_name!r}"))

    # lesson_id should be int
    lid = data.get("lesson_id")
    if not isinstance(lid, int):
        errors.append(_err(path, f"lesson_id must be int, got {type(lid).__name__}"))

    # fallback string
    fallback = data.get("fallback", "")
    if not isinstance(fallback, str) or not fallback.strip():
        errors.append(_err(path, "fallback must be a non-empty string"))

    # matches array
    matches = data.get("matches", [])
    if not isinstance(matches, list):
        errors.append(_err(path, "matches must be a list"))
        return errors

    all_keywords: list[str] = []
    for i, m in enumerate(matches):
        prefix = f"matches[{i}]"
        if not isinstance(m, dict):
            errors.append(_err(path, f"{prefix} must be an object"))
            continue
        kws = m.get("keywords", [])
        if not isinstance(kws, list) or not kws or not all(isinstance(k, str) and k for k in kws):
            errors.append(_err(path, f"{prefix}.keywords must be a non-empty list of non-empty strings"))
        else:
            all_keywords.extend(kws)
        rls = m.get("reply_lines", [])
        if not isinstance(rls, list) or not rls or not all(isinstance(r, str) for r in rls):
            errors.append(_err(path, f"{prefix}.reply_lines must be a non-empty list of strings"))
        # side_effect optional but if present must be valid
        se = m.get("side_effect")
        if se is None:
            continue
        if not isinstance(se, dict):
            errors.append(_err(path, f"{prefix}.side_effect must be an object or null"))
            continue
        action = se.get("action")
        if action not in ALLOWED_ACTIONS:
            errors.append(_err(path, f"{prefix}.side_effect.action {action!r} not in whitelist {sorted(ALLOWED_ACTIONS)}"))
        # picture art_id whitelist
        if action == "show_picture":
            art_id = se.get("art_id", "")
            if art_id not in ALLOWED_PICTURE_IDS:
                errors.append(_err(path, f"{prefix}.side_effect.art_id {art_id!r} not in {sorted(ALLOWED_PICTURE_IDS)}"))

    # Fallback should nudge toward at least one real keyword (so kid not dead-ended)
    if all_keywords and isinstance(fallback, str):
        fl = fallback.lower()
        if not any(kw.lower() in fl for kw in all_keywords):
            errors.append(_err(path, "fallback should mention at least one keyword from matches[] (kid hint)"))

    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    if not SANDBOX_DIR.is_dir():
        print(f"FAIL no sandbox dir at {SANDBOX_DIR}", file=sys.stderr)
        return 1

    files = sorted(SANDBOX_DIR.glob("*/lesson_*.json"))
    if not files:
        print("FAIL no sandbox JSONs found", file=sys.stderr)
        return 1

    total_errors: list[str] = []
    for f in files:
        errs = lint_file(f)
        if errs:
            total_errors.extend(errs)
        elif not args.quiet:
            print(f"  ok  {f.relative_to(ROOT)}")

    if total_errors:
        print()
        for e in total_errors:
            print(e, file=sys.stderr)
        print(f"\n{len(total_errors)} error(s) across {len(files)} file(s)", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"\nALL CLEAN — {len(files)} sandbox file(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
