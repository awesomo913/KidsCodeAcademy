"""Fix variations that list the same answer-option text twice.

A scan found ~59 variations (almost all q5 v6) where one wrong option is
duplicated, so the kid effectively sees only 3 distinct choices. We repair each
by replacing the SECOND copy with a distinct wrong option borrowed from another
variation of the SAME question -- so it stays on-topic and (bonus) already has
baked audio. Exactly one correct option is preserved.

Read-modify-write, idempotent. Run: python scripts/fix_duplicate_options.py
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("fix-dupe-options")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"


def wrong_pool(question: dict) -> list[dict]:
    """All distinct wrong-option dicts used anywhere in this question."""
    seen: set[str] = set()
    pool: list[dict] = []
    for v in question.get("variations") or []:
        for o in v.get("options") or []:
            t = str(o.get("text") or "")
            if not o.get("correct") and t and t not in seen:
                seen.add(t)
                pool.append(o)
    return pool


def fix_variation(v: dict, pool: list[dict]) -> bool:
    opts = v.get("options") or []
    texts = [str(o.get("text") or "") for o in opts]
    if len(texts) == len(set(texts)):
        return False
    present = set(texts)
    changed = False
    seen: set[str] = set()
    for i, o in enumerate(opts):
        t = str(o.get("text") or "")
        if t in seen:  # this is a duplicate slot -> replace it
            replacement = next(
                (p for p in pool if str(p.get("text")) not in present), None
            )
            if replacement is None:
                continue  # nothing distinct to swap in; leave as-is
            new_opt = {"text": replacement["text"], "correct": False}
            if replacement.get("_audio"):
                new_opt["_audio"] = replacement["_audio"]
            opts[i] = new_opt
            present.add(str(replacement["text"]))
            changed = True
        else:
            seen.add(t)
    return changed


def main() -> None:
    total_fixed = 0
    files_changed = 0
    for f in sorted(LESSONS_DIR.glob("lesson_*.json")):
        raw = f.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        data = json.loads(raw.decode("utf-8"))
        changed = False
        for q in data.get("questions") or []:
            pool = wrong_pool(q)
            for v in q.get("variations") or []:
                if fix_variation(v, pool):
                    total_fixed += 1
                    changed = True
        if changed:
            text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
            with open(f, "w", encoding="utf-8", newline="") as fh:
                fh.write(text.replace("\n", newline))
            files_changed += 1
            log.info("fixed %s", f.name)
    log.info("done: %d variations repaired across %d files", total_fixed, files_changed)


if __name__ == "__main__":
    main()
