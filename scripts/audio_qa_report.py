"""Generate an HTML audio QA report for parent spot-checking.

Pulls a random sample across three audio kinds — narration, question prompts,
answer options — and renders a single-file HTML page where the parent listens
to each clip and marks it Good or Bad. Findings export as a downloadable JSON.

Design notes:
- 100% client-side. No server, no network. Matches project's "no network" rule.
- Acronym-heavy lessons get 2x sampling weight (where Piper is most likely to
  mispronounce: AI/LLM/MCQ/etc.).
- Narration source text = the joined mascot_lines[] for each lesson; the actual
  synthesis source has acronyms spelled out (preprocess_acronyms.py), so we
  show BOTH the kid-visible text and the synthesis text per row.
- Output to audio_qa/report_<timestamp>.html — gitignored.

Usage:
    python scripts/audio_qa_report.py                    # 50 sample, mixed
    python scripts/audio_qa_report.py --n 100            # bigger sample
    python scripts/audio_qa_report.py --kind prompt      # only prompts
    python scripts/audio_qa_report.py --lesson 11 --n 30 # focus one lesson
    python scripts/audio_qa_report.py --seed 42          # reproducible
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("audio-qa")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
ASSETS_AUDIO = ROOT / "assets" / "audio"
QA_DIR = ROOT / "audio_qa"

# Match preprocess_acronyms.py — keep both lists in sync.
ACRONYMS: dict[str, str] = {
    "AI": "A I", "LLM": "L L M", "MCQ": "M C Q", "API": "A P I",
    "GPT": "G P T", "JSON": "J S O N", "HTML": "H T M L", "CSS": "C S S",
    "JS": "J S", "URL": "U R L", "PNG": "P N G", "SDK": "S D K",
    "CLI": "C L I", "GUI": "G U I", "TTS": "T T S", "RAM": "R A M",
    "CPU": "C P U", "GPU": "G P U",
}
ACRONYM_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in ACRONYMS) + r")\b")


def _spell(text: str) -> str:
    return ACRONYM_RE.sub(lambda m: ACRONYMS[m.group(1)], text)


def _has_acronym(text: str) -> bool:
    return bool(ACRONYM_RE.search(text))


@dataclass(frozen=True)
class AudioRow:
    """A single auditable audio entry."""
    row_id: str
    lesson_id: int
    lesson_title: str
    kind: str            # narration | prompt | option
    visible_text: str    # what the kid SEES (or hears as they read along)
    synthesis_text: str  # what was sent to Piper (acronyms spelled out)
    audio_path: str      # relative path under project root
    qid: str = ""
    var_idx: int = -1
    has_acronym: bool = False


def _emit_narration_rows(lesson: dict, lesson_id: int) -> list[AudioRow]:
    title = lesson.get("title", f"Lesson {lesson_id}")
    lines = lesson.get("mascot_lines", [])
    if not lines:
        return []
    visible = " ".join(lines)
    audio = f"assets/audio/lesson_{lesson_id:02d}.ogg"
    if not (ROOT / audio).is_file():
        return []
    return [AudioRow(
        row_id=f"L{lesson_id:02d}_narration",
        lesson_id=lesson_id,
        lesson_title=title,
        kind="narration",
        visible_text=visible,
        synthesis_text=_spell(visible),
        audio_path=audio,
        has_acronym=_has_acronym(visible),
    )]


def _emit_prompt_rows(lesson: dict, lesson_id: int) -> list[AudioRow]:
    title = lesson.get("title", f"Lesson {lesson_id}")
    rows: list[AudioRow] = []
    for q in lesson.get("questions", []):
        qid = q.get("id", "?")
        for vi, v in enumerate(q.get("variations", [])):
            audio = v.get("_audio")
            prompt = v.get("prompt", "")
            if not audio or not prompt:
                continue
            if not (ROOT / audio).is_file():
                continue
            rows.append(AudioRow(
                row_id=f"L{lesson_id:02d}_q{qid}_v{vi}",
                lesson_id=lesson_id,
                lesson_title=title,
                kind="prompt",
                visible_text=prompt,
                synthesis_text=_spell(prompt),
                audio_path=audio,
                qid=qid,
                var_idx=vi,
                has_acronym=_has_acronym(prompt),
            ))
    return rows


def _emit_option_rows(lesson: dict, lesson_id: int, seen: set[str]) -> list[AudioRow]:
    """Dedup options by audio path — same audio file may back many lessons."""
    title = lesson.get("title", f"Lesson {lesson_id}")
    rows: list[AudioRow] = []
    for q in lesson.get("questions", []):
        qid = q.get("id", "?")
        for vi, v in enumerate(q.get("variations", [])):
            for oi, opt in enumerate(v.get("options", [])):
                audio = opt.get("_audio")
                text = opt.get("text", "")
                if not audio or not text or audio in seen:
                    continue
                if not (ROOT / audio).is_file():
                    continue
                seen.add(audio)
                rows.append(AudioRow(
                    row_id=f"L{lesson_id:02d}_q{qid}_v{vi}_o{oi}",
                    lesson_id=lesson_id,
                    lesson_title=title,
                    kind="option",
                    visible_text=text,
                    synthesis_text=_spell(text),
                    audio_path=audio,
                    qid=qid,
                    var_idx=vi,
                    has_acronym=_has_acronym(text),
                ))
    return rows


def collect_rows(kinds: set[str], lesson_filter: int | None) -> list[AudioRow]:
    rows: list[AudioRow] = []
    seen_options: set[str] = set()
    files = sorted(LESSONS_DIR.glob("lesson_*.json"))
    for fp in files:
        m = re.match(r"lesson_(\d+)_", fp.name)
        if not m:
            continue
        lesson_id = int(m.group(1))
        if lesson_filter is not None and lesson_id != lesson_filter:
            continue
        with fp.open(encoding="utf-8") as fh:
            try:
                lesson = json.load(fh)
            except json.JSONDecodeError as exc:
                log.error("skip %s: %s", fp.name, exc)
                continue
        if "narration" in kinds:
            rows.extend(_emit_narration_rows(lesson, lesson_id))
        if "prompt" in kinds:
            rows.extend(_emit_prompt_rows(lesson, lesson_id))
        if "option" in kinds:
            rows.extend(_emit_option_rows(lesson, lesson_id, seen_options))
    return rows


def weighted_sample(rows: list[AudioRow], n: int, rng: random.Random) -> list[AudioRow]:
    """Acronym-heavy rows get 2x weight, others 1x."""
    if len(rows) <= n:
        return list(rows)
    weights = [2.0 if r.has_acronym else 1.0 for r in rows]
    # weighted-without-replacement via key: -log(U) / w  (Efraimidis-Spirakis)
    keys = [(-1.0 * (rng.random() ** (1.0 / w)), idx) for idx, w in enumerate(weights)]
    keys.sort()
    chosen = [rows[idx] for _, idx in keys[:n]]
    return chosen


# ---------- HTML render ----------

_HTML_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Kids Code Academy — Audio QA Report</title>
<style>
:root {
  --bg: #faf7f2; --fg: #2a2a2a; --good: #4caf50; --bad: #e53935;
  --muted: #999; --card: #fff; --border: #ddd; --highlight: #fff7cf;
  --acronym: #ffd95e;
}
* { box-sizing: border-box; }
body { font: 15px/1.4 "Segoe UI", sans-serif; background: var(--bg); color: var(--fg); margin: 0; padding: 20px; }
h1 { margin: 0 0 6px; }
.sub { color: var(--muted); margin-bottom: 18px; }
.toolbar { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 14px; margin-bottom: 18px; position: sticky; top: 8px; z-index: 10; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.counts { display: inline-flex; gap: 12px; align-items: center; margin-right: 18px; }
.chip { display: inline-block; padding: 3px 10px; border-radius: 12px; background: #eee; font-size: 13px; }
.chip.good { background: var(--good); color: #fff; }
.chip.bad { background: var(--bad); color: #fff; }
.chip.acronym { background: var(--acronym); color: #2a2a2a; font-weight: 600; }
button { font: inherit; padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border); background: #f5f5f5; cursor: pointer; }
button:hover { background: #eee; }
button.primary { background: #6c5ce7; color: #fff; border-color: #6c5ce7; }
button.good { background: var(--good); color: #fff; border-color: var(--good); }
button.bad { background: var(--bad); color: #fff; border-color: var(--bad); }
.row { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 14px; margin-bottom: 12px; display: grid; grid-template-columns: 110px 1fr 200px; gap: 14px; align-items: start; }
.row[data-verdict="good"] { background: #e8f5e9; border-color: var(--good); }
.row[data-verdict="bad"] { background: #ffebee; border-color: var(--bad); }
.row .meta { font-size: 12px; color: var(--muted); }
.row .text { font-size: 15px; }
.row .synth { font-size: 13px; color: #666; font-family: ui-monospace, monospace; margin-top: 4px; padding: 4px 6px; background: #f7f7f7; border-radius: 4px; display: none; }
.row[data-show-synth="1"] .synth { display: block; }
.row .actions { display: flex; flex-direction: column; gap: 6px; }
.row audio { width: 100%; height: 32px; }
.kind { font-weight: 600; }
.kind.narration { color: #5e35b1; }
.kind.prompt    { color: #d84315; }
.kind.option    { color: #00838f; }
#exportArea { background: #f5f5f5; padding: 10px; border-radius: 6px; font-family: ui-monospace, monospace; font-size: 12px; max-height: 200px; overflow: auto; display: none; white-space: pre-wrap; }
</style>
</head>
<body>
<h1>Kids Code Academy — Audio QA</h1>
<div class="sub">Tap ▶ to listen. Mark each clip ✓ Good or ✗ Bad. Reasons help us re-bake.</div>
"""

_HTML_TOOLBAR = """<div class="toolbar">
  <div class="counts">
    <span class="chip" id="totalChip"></span>
    <span class="chip good" id="goodChip">✓ 0</span>
    <span class="chip bad" id="badChip">✗ 0</span>
  </div>
  <button onclick="toggleSynth()">Show synthesis text</button>
  <button class="primary" onclick="exportJSON()">Export findings</button>
  <button onclick="resetAll()">Reset all</button>
  <pre id="exportArea"></pre>
</div>
"""

_BAD_REASONS = ["garbled", "wrong word", "sounds robotic", "wrong tone", "too fast", "too slow", "other"]


def _row_html(row: AudioRow) -> str:
    visible_esc = html.escape(row.visible_text)
    synth_esc = html.escape(row.synthesis_text)
    chips: list[str] = []
    if row.has_acronym:
        chips.append('<span class="chip acronym">acronym</span>')
    chips_html = " ".join(chips)
    return f"""<div class="row" id="row-{row.row_id}" data-row-id="{row.row_id}">
  <div class="meta">
    <div>L{row.lesson_id:02d}</div>
    <div class="kind {row.kind}">{row.kind}</div>
    {chips_html}
  </div>
  <div>
    <div class="text">{visible_esc}</div>
    <div class="synth">→ {synth_esc}</div>
    <audio controls preload="none" src="../{row.audio_path}"></audio>
  </div>
  <div class="actions">
    <button class="good" onclick="rate('{row.row_id}', 'good')">✓ Sounds good</button>
    <button class="bad" onclick="rate('{row.row_id}', 'bad')">✗ Bad</button>
  </div>
</div>"""


_HTML_SCRIPT_TMPL = """<script>
const STORAGE_KEY = "kca_audio_qa_v1";
const TOTAL = __TOTAL__;
const REASONS = __REASONS__;
const SESSION_ID = "__SESSION_ID__";

function load() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
  catch (e) { return {}; }
}
function save(data) { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }

function rate(rowId, verdict) {
  const data = load();
  let reason = "";
  if (verdict === "bad") {
    const choices = REASONS.map((r, i) => `${i+1}. ${r}`).join("\\n");
    const ans = prompt("Why is this bad?\\n\\n" + choices + "\\n\\nEnter number 1-" + REASONS.length + " (or your own reason):");
    if (ans === null) return;
    const num = parseInt(ans, 10);
    reason = (Number.isFinite(num) && num >= 1 && num <= REASONS.length) ? REASONS[num - 1] : ans.trim();
  }
  data[rowId] = { verdict, reason, ts: new Date().toISOString() };
  save(data);
  applyVerdict(rowId, verdict);
  refreshCounts();
}

function applyVerdict(rowId, verdict) {
  const el = document.getElementById("row-" + rowId);
  if (el) el.dataset.verdict = verdict;
}

function refreshCounts() {
  const data = load();
  let good = 0, bad = 0;
  for (const k of Object.keys(data)) {
    if (data[k].verdict === "good") good++;
    else if (data[k].verdict === "bad") bad++;
  }
  document.getElementById("totalChip").textContent = (good + bad) + " / " + TOTAL + " rated";
  document.getElementById("goodChip").textContent = "✓ " + good;
  document.getElementById("badChip").textContent = "✗ " + bad;
}

function toggleSynth() {
  document.querySelectorAll(".row").forEach(r => {
    r.dataset.showSynth = r.dataset.showSynth === "1" ? "0" : "1";
  });
}

function exportJSON() {
  const data = load();
  const out = { session_id: SESSION_ID, total_rows: TOTAL, ratings: data };
  const text = JSON.stringify(out, null, 2);
  const area = document.getElementById("exportArea");
  area.style.display = "block";
  area.textContent = text;
  // also trigger download
  const blob = new Blob([text], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "kca_audio_qa_" + SESSION_ID.replace(/[:.]/g, "-") + ".json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);
}

function resetAll() {
  if (!confirm("Clear all ratings for this report?")) return;
  localStorage.removeItem(STORAGE_KEY);
  document.querySelectorAll(".row").forEach(r => delete r.dataset.verdict);
  refreshCounts();
}

document.addEventListener("DOMContentLoaded", () => {
  const data = load();
  for (const rowId of Object.keys(data)) {
    applyVerdict(rowId, data[rowId].verdict);
  }
  refreshCounts();
});
</script>
</body></html>"""


def render_html(rows: list[AudioRow], session_id: str) -> str:
    body_parts = [_HTML_HEAD, _HTML_TOOLBAR]
    for r in rows:
        body_parts.append(_row_html(r))
    script = (
        _HTML_SCRIPT_TMPL
        .replace("__TOTAL__", str(len(rows)))
        .replace("__REASONS__", json.dumps(_BAD_REASONS))
        .replace("__SESSION_ID__", session_id)
    )
    body_parts.append(script)
    return "\n".join(body_parts)


def main() -> int:
    p = argparse.ArgumentParser(description="Generate an audio QA report.")
    p.add_argument("--n", type=int, default=50, help="sample size")
    p.add_argument("--kind", choices=["narration", "prompt", "option", "all"], default="all")
    p.add_argument("--lesson", type=int, default=None, help="filter to one lesson id")
    p.add_argument("--seed", type=int, default=None, help="RNG seed for reproducible samples")
    p.add_argument("--out", type=Path, default=None, help="output HTML path")
    args = p.parse_args()

    kinds = {"narration", "prompt", "option"} if args.kind == "all" else {args.kind}
    rng = random.Random(args.seed)

    log.info("collecting rows for kinds=%s lesson=%s", sorted(kinds), args.lesson)
    rows = collect_rows(kinds, args.lesson)
    log.info("collected %d candidate rows", len(rows))
    if not rows:
        log.error("no rows found — check that audio files exist + lesson schemas are valid")
        return 2

    sample = weighted_sample(rows, args.n, rng)
    sample.sort(key=lambda r: (r.lesson_id, r.kind, r.row_id))
    log.info("sampled %d rows (acronym-heavy: %d)", len(sample), sum(1 for r in sample if r.has_acronym))

    QA_DIR.mkdir(parents=True, exist_ok=True)
    session_id = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    out = args.out or (QA_DIR / f"report_{session_id.replace(':', '-')}.html")
    out.write_text(render_html(sample, session_id), encoding="utf-8")
    log.info("wrote %s", out)
    log.info("open in browser:  %s", out.absolute().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
