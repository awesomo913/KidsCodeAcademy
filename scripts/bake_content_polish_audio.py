"""Bake only narration changed by polish_content_quality.py."""
from __future__ import annotations

import json
import os
import shutil
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "logs" / "content_polish_audio_manifest.json"


def _bake_one(task: tuple[str, str, str]) -> tuple[str, bool, str]:
    """Worker: load one Piper voice per process and bake one unique phrase."""
    rel, spoken_text, ffmpeg = task
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compress_audio_ogg import convert_wav_to_ogg
    from piper_bake import synth

    ogg = ROOT / rel
    wav = ogg.with_suffix(".wav")
    try:
        ok = synth(spoken_text, wav) and convert_wav_to_ogg(Path(ffmpeg), wav, ogg)
        return rel, bool(ok), ""
    except Exception as exc:
        return rel, False, str(exc)


def main() -> int:
    if not MANIFEST.is_file():
        print("no content-polish audio manifest; nothing to do")
        return 0
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compress_audio_ogg import _find_ffmpeg, convert_wav_to_ogg
    from piper_bake import is_available, synth

    if not is_available():
        print("Piper voice/runtime is unavailable", file=sys.stderr)
        return 1
    ffmpeg = _find_ffmpeg()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prompts = dict(manifest.get("prompts") or {})
    options = dict(manifest.get("options") or {})
    cutoff_ns = MANIFEST.stat().st_mtime_ns
    groups: dict[str, list[str]] = defaultdict(list)
    for rel, text in prompts.items():
        groups[str(text)].append(rel)

    # A replay often speaks the same prompt from ten different file paths.
    # Synthesize each unique phrase once, then copy the exact encoded clip.
    representatives: dict[str, list[str]] = {}
    copied = 0
    for spoken_text, paths in groups.items():
        freshly_baked = next((rel for rel in paths if (ROOT / rel).is_file() and (ROOT / rel).stat().st_mtime_ns >= cutoff_ns), None)
        if freshly_baked:
            for rel in paths:
                if rel != freshly_baked:
                    (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / freshly_baked, ROOT / rel)
                    copied += 1
            continue
        representatives[paths[0]] = paths

    tasks = [(rel, next(text for text, paths in groups.items() if paths is destinations), str(ffmpeg))
             for rel, destinations in representatives.items()]
    # Hashed option paths are content-addressed, so an existing file already
    # speaks the right text. Only missing option clips need synthesis.
    for rel, text in options.items():
        if not (ROOT / rel).is_file():
            tasks.append((rel, str(text), str(ffmpeg)))

    errors = 0
    completed = 0
    workers = max(1, min(4, (os.cpu_count() or 2) // 2))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_bake_one, task): task for task in tasks}
        for future in as_completed(futures):
            rel, ok, err = future.result()
            completed += 1
            if not ok:
                errors += 1
                print(f"FAILED {rel}: {err}", file=sys.stderr, flush=True)
            elif rel in representatives:
                for destination in representatives[rel][1:]:
                    (ROOT / destination).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / rel, ROOT / destination)
                    copied += 1
            if completed % 25 == 0 or completed == len(tasks):
                print(f"baked {completed}/{len(tasks)} unique phrases", flush=True)
    print(f"content-polish audio: {len(tasks) - errors} unique phrases ok, {copied} replay copies, {errors} errors")
    if not errors:
        MANIFEST.unlink(missing_ok=True)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
