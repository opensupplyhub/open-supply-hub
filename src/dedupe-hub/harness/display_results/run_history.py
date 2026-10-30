#!/usr/bin/env python3
"""Run history and per-slice outcome bars. OSDEV-3277.

Every slice_report.py run can be saved as a record in a history file (JSON
lines). This module reads that file and draws it: one section per slice
(country, lookalike class, ...), and under each section one bar per run, oldest
first. Every bar adds up to 100% of that slice's evaluation pairs and is split
into the outcomes below. Run it again with a new model or training file and a new
bar appears under every country.

Segments, left to right:
  never considered  a real match the rules never retrieved (a duplicate).
                    NOT measurable from labeled pairs, because every pair was
                    already a candidate the old matcher surfaced. It appears
                    only when a record carries a not_retrieved count, which
                    needs a per-upload run (measure_fanout.py).
  scored too low    a real match that was considered but scored below the floor
                    (also a duplicate)
  human review      scored between the floor and the auto bar
  wrongly matched   at or above the auto bar but not a match (a wrong merge)
  correctly matched at or above the auto bar and a real match
  left alone        not a match, scored below the floor (correct, no action)

Runs are only drawn together when they were graded on the same evaluation set
(same checksum, same exact-match setting); the page says how many others are
hidden. Pure stdlib.
"""
import datetime
import hashlib
import html
import json
import os

# Left to right in every bar: (count key, long label, short label, bar letter, css class)
SEGMENTS = [
    ("not_retrieved", "Real match never considered (duplicate)", "never considered", "N", "never"),
    ("missed", "Real match considered but scored too low (duplicate)", "scored too low", "L", "low"),
    ("review", "Sent to a human to review", "human review", "R", "review"),
    ("auto_bad", "Wrongly matched", "wrongly matched", "W", "wrong"),
    ("auto_ok", "Correctly matched", "correctly matched", "C", "correct"),
    ("none_ok", "Correctly left alone (not a match, not offered)", "correctly left alone", ".", "left"),
]


def sha256_of(path):
    """Hex SHA-256 of a file, read in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_utc():
    """Current UTC time as an ISO string without microseconds."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def load_runs(path):
    """Read the history file; a missing file is an empty history."""
    if not path or not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def save_runs(path, runs):
    """Write the whole history back, one JSON record per line."""
    with open(path, "w") as f:
        for r in runs:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def add_runs(path, new_runs):
    """Add records to the history. A record with the same run_id and view as an
    existing one replaces it, so re-running a label updates its bar instead of
    adding a duplicate. Returns the full history."""
    existing = load_runs(path)
    keys = {(r["run_id"], r["view"]) for r in new_runs}
    kept = [r for r in existing if (r["run_id"], r["view"]) not in keys]
    runs = kept + list(new_runs)
    save_runs(path, runs)
    return runs


def parts(counts):
    """The segments a slice has, in bar order, as (key, long, short, letter, css,
    count). A segment whose count is None (not measurable for this run) is
    left out."""
    out = []
    for key, long_, short, letter, css in SEGMENTS:
        c = counts.get(key)
        if c is not None:
            out.append((key, long_, short, letter, css, c))
    return out


def total_of(counts):
    """Number of pairs the bar adds up to."""
    return sum(p[-1] for p in parts(counts))


def bar_letters(counts, width=48):
    """A text bar, one letter per segment, scaled to `width` characters with the
    largest-remainder rule so the letters always add up to exactly `width`."""
    ps = parts(counts)
    total = sum(p[-1] for p in ps)
    if not total:
        return "(no pairs)"
    raw = [p[-1] / total * width for p in ps]
    take = [int(x) for x in raw]
    order = sorted(range(len(ps)), key=lambda i: raw[i] - take[i], reverse=True)
    for i in order[:width - sum(take)]:
        take[i] += 1
    return "".join(p[3] * t for p, t in zip(ps, take))


def legend_text():
    """One-line key for the text bars."""
    return ("Key: N never considered (only with --retrieval) | L real match scored too low | "
            "R human review | W wrongly matched | C correctly matched | "
            ". correctly left alone")


def text_bars(run, slice_names=None):
    """Lines of text bars for one run record (one view), a bar per slice with
    percentages and counts."""
    lines = []
    for name, counts in run["slices"].items():
        if slice_names is not None and name not in slice_names:
            continue
        total = total_of(counts)
        lines.append(f"{name}  ({total} pairs)")
        lines.append(f"  [{bar_letters(counts)}]")
        if total:
            detail = " | ".join(f"{p[2]} {p[5]} ({p[5] / total:.1%})" for p in parts(counts))
            lines.append(f"  {detail}")
        lines.append("")
    return lines


CSS = """
:root{--bg:#fff;--fg:#1f2328;--muted:#656d76;--line:#d0d7de;--card:#f6f8fa;
--never:#7a3e06;--low:#c2691c;--review:#e3b341;--wrong:#cf222e;--correct:#1f9d63;--left:#adb5bd}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--muted:#8d96a0;--line:#30363d;
--card:#161b22;--never:#b5651d;--low:#e08a3c;--review:#d4a72c;--wrong:#f85149;--correct:#3fb950;--left:#6e7681}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:22px;margin:0 0 4px} h2{font-size:16px;margin:28px 0 8px;padding-top:12px;border-top:1px solid var(--line)}
h2 small{font-weight:400;color:var(--muted);margin-left:8px}
.lede,.note,.cap,.meta{color:var(--muted)} .note{font-size:13px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;margin:12px 0;font-size:13px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:14px;height:14px;border-radius:3px;display:inline-block}
.toggle{margin:12px 0} .toggle button{font:inherit;padding:4px 12px;margin-right:6px;border:1px solid var(--line);
background:var(--card);color:var(--fg);border-radius:6px;cursor:pointer}
.toggle button[aria-pressed=true]{border-color:var(--fg);font-weight:600}
.run{display:grid;grid-template-columns:200px 1fr;gap:4px 12px;margin:6px 0 10px}
.runlabel b{display:block;overflow-wrap:anywhere} .meta{font-size:12px}
.bar{display:flex;height:28px;border-radius:4px;overflow:hidden;background:var(--card);border:1px solid var(--line)}
.seg{display:flex;align-items:center;justify-content:center;font-size:12px;color:#fff;overflow:hidden;white-space:nowrap}
.seg.review,.seg.left{color:#111}
.never{background:repeating-linear-gradient(45deg,var(--never),var(--never) 4px,transparent 4px,transparent 8px)}
.low{background:var(--low)} .review{background:var(--review)} .wrong{background:var(--wrong)}
.correct{background:var(--correct)} .left{background:var(--left)}
.cap{font-size:12px;margin-top:3px}
@media (max-width:640px){.run{grid-template-columns:1fr}}
"""

JS = """
document.querySelectorAll('.toggle button').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.view').forEach(function(v){v.hidden=(v.dataset.view!==b.dataset.v);});
    document.querySelectorAll('.toggle button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});
  });
});
"""

VIEW_NOTE = {
    "all": "All labels: every rejected pair counts as a non-match (the conservative view).",
    "clean": "Clean labels: rejections where the moderator picked a sibling instead are dropped, "
             "so very few true non-matches remain in some countries.",
}


def _run_row(run, counts):
    """HTML for one run's bar under one slice."""
    ps = parts(counts)
    total = sum(p[-1] for p in ps)
    segs, cap = [], []
    for key, long_, short, letter, css, c in ps:
        pct = c / total * 100 if total else 0
        label = f"{pct:.0f}%" if pct >= 7 else ""
        segs.append(f'<span class="seg {css}" style="width:{pct:.3f}%" '
                    f'title="{html.escape(long_)}: {c} ({pct:.1f}%)">{label}</span>')
        cap.append(f"{html.escape(short)} {c} ({pct:.1f}%)")
    op = run.get("operating_point", {})
    tr = run.get("training") or {}
    meta = [run.get("when", "")[:10], f"bar {op.get('auto')} / floor {op.get('floor')}"]
    if tr.get("file"):
        meta.append(f"{tr['file']} ({tr.get('match', '?')} match, {tr.get('distinct', '?')} distinct)")
    return (f'<div class="run"><div class="runlabel"><b>{html.escape(run["run_id"])}</b>'
            f'<span class="meta">{html.escape(" · ".join(str(m) for m in meta if m))}</span></div>'
            f'<div><div class="bar" role="img" aria-label="{html.escape("; ".join(cap))}">'
            f'{"".join(segs)}</div><div class="cap">{" · ".join(cap)}</div></div></div>')


def render_html(runs, title="Outcome by country, one bar per run"):
    """Return a standalone HTML page: one section per slice, one bar per run.

    Only runs graded on the same evaluation set as the newest run are drawn;
    the page says how many others were hidden."""
    if not runs:
        return "<!doctype html><title>No runs</title><p>No runs recorded yet.</p>"
    runs = sorted(runs, key=lambda r: r.get("when", ""))
    ref = runs[-1]
    ref_key = (ref["dataset"].get("sha256"), ref["dataset"].get("exclude_exact"))
    shown = [r for r in runs
             if (r["dataset"].get("sha256"), r["dataset"].get("exclude_exact")) == ref_key]
    hidden = len(runs) - len(shown)
    views = [v for v in ("all", "clean") if any(r["view"] == v for r in shown)]
    ds = ref["dataset"]
    sha = (ds.get("sha256") or "none (hash split, not frozen)")[:12]
    have_never = any(c.get("not_retrieved") is not None
                     for r in shown for c in r["slices"].values())

    legend = "".join(f'<span><i class="sw {css}"></i>{html.escape(long_)}</span>'
                     for key, long_, short, letter, css in SEGMENTS
                     if key != "not_retrieved" or have_never)
    parts_html = []
    for v in views:
        sections = []
        names = []
        for r in shown:
            if r["view"] == v:
                names += [n for n in r["slices"] if n not in names]
        for name in names:
            rows = [_run_row(r, r["slices"][name]) for r in shown
                    if r["view"] == v and name in r["slices"]]
            n = next((total_of(r["slices"][name]) for r in shown
                      if r["view"] == v and name in r["slices"]), 0)
            sections.append(f'<section><h2>{html.escape(name)}<small>{n} pairs</small></h2>'
                            f'{"".join(rows)}</section>')
        hid = "" if v == views[0] else " hidden"
        parts_html.append(f'<div class="view" data-view="{v}"{hid}>'
                          f'<p class="note">{html.escape(VIEW_NOTE[v])}</p>{"".join(sections)}</div>')
    buttons = "".join(f'<button data-v="{v}" aria-pressed="{"true" if i == 0 else "false"}">'
                      f'{"All labels" if v == "all" else "Clean labels"}</button>'
                      for i, v in enumerate(views))
    never_note = ("" if have_never else
                  " “Real match never considered” is not shown: labeled pairs cannot measure it "
                  "(every pair was already a candidate). It needs a per-upload run.")
    hidden_note = (f" {hidden} earlier run(s) graded on a different evaluation set are hidden."
                   if hidden else "")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>Outcome by country</title><style>{CSS}</style></head><body><main>'
            f'<h1>{html.escape(title)}</h1>'
            f'<p class="lede">Each bar is 100% of one slice’s evaluation pairs. A new run adds a bar '
            f'under every country.</p><div class="legend">{legend}</div>'
            f'<p class="note">Evaluation set {html.escape(sha)}, '
            f'exact matches excluded: {"yes" if ds.get("exclude_exact") else "no"}, '
            f'{len(shown)} run(s) shown.{html.escape(hidden_note)}{html.escape(never_note)}</p>'
            f'<div class="toggle">{buttons}</div>{"".join(parts_html)}</main>'
            f'<script>{JS}</script></body></html>')
