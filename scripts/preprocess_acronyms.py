"""Re-bake any wav whose source text contains a tech acronym Piper mispronounces.

Piper reads "LLM" as one weird syllable. Same for "MCQ", "API", "AI", "JSON",
"GPT", "URL", "HTML", "CSS", "JS". Fix: spell them out (L L M) before
synthesis, so the kid hears "ell ell em".

Walks every option text + question prompt, finds matches against the acronym
list, and re-bakes ONLY the affected wavs with the spelled-out version.

Original lesson JSON is NOT changed (kid still SEES "LLM"). Only the audio
generation source string is preprocessed before piper.synth().

Usage:
    python scripts/preprocess_acronyms.py            # incremental
    python scripts/preprocess_acronyms.py --force    # re-bake all matches
    python scripts/preprocess_acronyms.py --dry-run  # show matches only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("acronym")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
OPT_DIR = ROOT / "assets" / "audio" / "o"
Q_DIR   = ROOT / "assets" / "audio" / "q"

# Acronyms Piper handles poorly. Add more as the kid encounters them.
# Match whole-word, case-sensitive uppercase form only (so "Use" doesn't fire).
ACRONYMS: dict[str, str] = {
    "AI":    "A I",
    "LLM":   "L L M",
    "MCQ":   "M C Q",
    "API":   "A P I",
    "GPT":   "G P T",
    "JSON":  "J S O N",
    "HTML":  "H T M L",
    "CSS":   "C S S",
    "JS":    "J S",
    "URL":   "U R L",
    "PNG":   "P N G",
    "SDK":   "S D K",
    "CLI":   "C L I",
    "GUI":   "G U I",
    "TTS":   "T T S",
    "RAM":   "R A M",
    "CPU":   "C P U",
    "GPU":   "G P U",
}

# Compile one regex: \b(?:AI|LLM|...)\b — uppercase-only.
ACRONYM_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in ACRONYMS) + r")\b")


def _hash_text(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def _spell(text: str) -> tuple[str, list[str]]:
    """Replace each acronym match with its spelled-out form. Returns (new_text, hits)."""
    hits: list[str] = []
    def sub(m: re.Match) -> str:
        a = m.group(1)
        hits.append(a)
        return ACRONYMS[a]
    new = ACRONYM_RE.sub(sub, text)
    return new, hits


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from piper_bake import is_available, synth  # type: ignore

    if not is_available():
        log.error("Piper not available — check voices/en_US-amy-medium.onnx")
        return 1

    # Walk all option texts (deduped by hash) + all variation prompts
    matches: dict[Path, str] = {}   # out_path → spelled-out text to bake
    seen_text: set[str] = set()
    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    for lf in files:
        try:
            data = json.loads(lf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.error("bad JSON %s: %s", lf.name, exc)
            continue
        num = lf.stem.split("_")[1]
        for q in data.get("questions") or []:
            qid = q.get("id") or "q?"
            for vidx, v in enumerate(q.get("variations") or []):
                # Question prompt
                prompt = (v.get("prompt") or "").strip()
                if prompt and ACRONYM_RE.search(prompt) and prompt not in seen_text:
                    seen_text.add(prompt)
                    new, hits = _spell(prompt)
                    out = ROOT / f"assets/audio/q/lesson_{num}_{qid}_v{vidx}.wav"
                    matches[out] = new
                # Option texts
                for opt in v.get("options") or []:
                    text = (opt.get("text") or "").strip()
                    if text and ACRONYM_RE.search(text) and text not in seen_text:
                        seen_text.add(text)
                        new, hits = _spell(text)
                        out = ROOT / f"assets/audio/o/{_hash_text(text)}.wav"
                        matches[out] = new

    log.info("found %d unique strings with acronyms", len(matches))
    if args.dry_run:
        for out, new in list(matches.items())[:20]:
            log.info("  %s -> %r", out.name, new[:60])
        log.info("(dry-run, no writes)")
        return 0

    baked = 0
    skipped = 0
    errors = 0
    for out, new_text in matches.items():
        if not args.force and out.is_file():
            # Re-bake only if the wav is older than this script (cheap freshness gate)
            script_mtime = Path(__file__).stat().st_mtime
            if out.stat().st_mtime >= script_mtime:
                skipped += 1
                continue
        try:
            ok = synth(new_text, out)
        except (OSError, RuntimeError) as exc:
            log.error("synth FAIL %s: %s", out.name, exc)
            errors += 1
            continue
        if ok:
            baked += 1

    log.info("DONE -- baked=%d skipped=%d errors=%d", baked, skipped, errors)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
