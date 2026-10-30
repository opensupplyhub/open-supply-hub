#!/usr/bin/env python3
"""Per-upload outcome bars. OSDEV-3277.

Draws what finally happens to each upload, using the six outcomes classified by
outcomes.py. Uploads fall into two groups that are never mixed in one bar,
because they answer different questions:

  has_match  uploads that have a confirmed match: did we find the existing
             facility?  correctly matched | human review (below the bar) |
             human review (several above the bar) | duplicate | incorrect match
  new        genuinely new uploads (no existing facility): did we leave them
             alone?  correctly new | human review (below) | human review (above)
             | incorrect match

Each bar adds up to 100% of its group. The reasons inside an outcome (for
example why a duplicate happened) are shown on hover and in the caption.

A run record looks like:
  {"run_id", "when", "unit": "uploads", "operating_point": {"auto", "floor"},
   "illustrative": bool, "slices": {slice name: {group: {"n", "counts",
   "causes"}}}}
Pure stdlib; reuses the page styling from run_history.py.
"""
import html
from collections import Counter, defaultdict

from run_history import CSS as BASE_CSS, now_utc

# Left to right in a bar: (key, label, plain-language meaning, css class).
OUTCOMES = [
    ("correctly_matched", "Correctly matched",
     "Linked automatically to the right facility.", "o-ok"),
    ("correctly_new", "Correctly new",
     "There was no existing facility, and a new one was created.", "o-new"),
    ("review_below_bar", "Human review, below the auto bar",
     "Sent to a person: the best candidate scored between the floor and the auto bar.",
     "o-revlow"),
    ("review_above_bar", "Human review, several above the bar",
     "Sent to a person: two or more candidates cleared the auto bar and nothing broke the tie.",
     "o-revhigh"),
    ("duplicate", "Duplicate",
     "An existing facility was not linked: a new one is created, or a person is shown "
     "candidates that do not include the right one.", "o-dup"),
    ("incorrect_match", "Incorrect match",
     "Linked automatically to the wrong facility (or to one when there was none).",
     "o-wrong"),
]

CAUSE_TEXT = {
    "alone_above_bar": "alone above the bar",
    "exact_string_tie_break": "won on an exact text match",
    "margin_win": "won by a clear margin over the next candidate",
    "nothing_reached_floor": "nothing reached the floor",
    "never_retrieved": "true match never retrieved",
    "scored_below_floor": "true match scored below the floor",
    "no_true_match_exists": "a genuinely new upload was linked to an existing facility",
    "true_match_not_chosen": "true match was on the list but another was chosen",
    "true_match_never_retrieved": "true match never retrieved",
    "true_match_scored_below_floor": "true match scored below the floor",
}

GROUPS = [("has_match", "Uploads that have a confirmed match"),
          ("new", "Genuinely new uploads (no existing facility)")]

EXTRA_CSS = """
.o-ok{background:var(--correct)} .o-new{background:#2f81f7} .o-revlow{background:#f0d264}
.o-revhigh{background:#d19a00} .o-dup{background:var(--low)} .o-wrong{background:var(--wrong)}
.seg.o-revlow,.seg.o-revhigh{color:#111}
.banner{background:#fff3cd;color:#664d03;border:1px solid #ffda6a;border-radius:6px;padding:10px 14px;margin:12px 0}
@media (prefers-color-scheme:dark){.banner{background:#3a2f0b;color:#f0d98a;border-color:#6b5a1e}}
.grp{font-size:12px;color:var(--muted);margin:6px 0 2px}
.why{color:var(--muted)}
details{margin:10px 0;font-size:14px} details p{margin:6px 0}
"""


def aggregate(results):
    """Turn classified uploads into the counts a bar needs.

    `results` is an iterable of (group, outcome, cause) with group 'has_match' or
    'new'. Returns {group: {"n": uploads, "counts": {outcome: n},
    "causes": {outcome: {cause: n}}}}.
    """
    out = {g: {"n": 0, "counts": Counter(), "causes": defaultdict(Counter)}
           for g, _ in GROUPS}
    for group, outcome, cause in results:
        out[group]["n"] += 1
        out[group]["counts"][outcome] += 1
        out[group]["causes"][outcome][cause] += 1
    return {g: {"n": d["n"], "counts": dict(d["counts"]),
                "causes": {k: dict(v) for k, v in d["causes"].items()}}
            for g, d in out.items()}


def make_record(run_id, slice_results, auto, floor, illustrative=False, when=None):
    """Build one history record from {slice name: [(group, outcome, cause), ...]}."""
    return {"run_id": run_id, "when": when or now_utc(), "unit": "uploads",
            "operating_point": {"auto": auto, "floor": floor},
            "illustrative": illustrative,
            "slices": {name: aggregate(res) for name, res in slice_results.items()}}


def _group_block(group_label, data):
    """HTML for one bar (one group of uploads, one run), with its caption."""
    n = data["n"]
    if not n:
        return ""
    segs, cap, plain = [], [], []
    for key, name, _meaning, css in OUTCOMES:
        c = data["counts"].get(key, 0)
        if not c:
            continue
        pct = c / n * 100
        plain.append(f"{name} {c} ({pct:.1f}%)")
        causes = data["causes"].get(key, {})
        cause_txt = "; ".join(f"{CAUSE_TEXT.get(k, k)} {v}"
                              for k, v in sorted(causes.items(), key=lambda kv: -kv[1]))
        title = f"{name}: {c} ({pct:.1f}%)" + (f". {cause_txt}" if cause_txt else "")
        label = f"{pct:.0f}%" if pct >= 7 else ""
        segs.append(f'<span class="seg {css}" style="width:{pct:.3f}%" '
                    f'title="{html.escape(title)}">{label}</span>')
        why = (f' <span class="why">[{html.escape(cause_txt)}]</span>'
               if cause_txt and not key.startswith("review") else "")
        cap.append(f"<b>{html.escape(name)}</b> {c} ({pct:.1f}%){why}")
    aria = f"{group_label}, {n} uploads: " + "; ".join(plain)
    return (f'<div class="grp">{html.escape(group_label)}, {n} uploads</div>'
            f'<div class="bar" role="img" aria-label="{html.escape(aria)}">{"".join(segs)}</div>'
            f'<div class="cap">{" · ".join(cap)}</div>')


def render_upload_html(runs, title="What happens to uploads, one bar per run"):
    """Return a standalone HTML page: one section per slice, and under it one
    pair of bars (confirmed-match uploads, new uploads) per run, oldest first."""
    runs = sorted((r for r in runs if r.get("unit") == "uploads"), key=lambda r: r["when"])
    if not runs:
        return "<!doctype html><title>No runs</title><p>No per-upload runs recorded yet.</p>"
    names = []
    for r in runs:
        names += [n for n in r["slices"] if n not in names]
    legend = "".join(f'<span title="{html.escape(m)}"><i class="sw {css}"></i>{html.escape(n)}</span>'
                     for _k, n, m, css in OUTCOMES)
    meanings = "".join(f"<p><b>{html.escape(n)}.</b> {html.escape(m)}</p>"
                       for _k, n, m, _c in OUTCOMES)
    sections = []
    for name in names:
        rows = []
        for r in runs:
            if name not in r["slices"]:
                continue
            op = r["operating_point"]
            body = "".join(_group_block(label, r["slices"][name][g]) for g, label in GROUPS)
            rows.append(f'<div class="run"><div class="runlabel"><b>{html.escape(r["run_id"])}</b>'
                        f'<span class="meta">{html.escape(r["when"][:10])} · bar {op["auto"]} / '
                        f'floor {op["floor"]}</span></div><div>{body}</div></div>')
        sections.append(f'<section><h2>{html.escape(name)}</h2>{"".join(rows)}</section>')
    banner = ('<div class="banner"><b>ILLUSTRATIVE.</b> These are made-up uploads run through '
              'the real outcome rule, to show how the page reads. They are not results.</div>'
              if any(r.get("illustrative") for r in runs) else "")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>Upload outcomes by country</title><style>{BASE_CSS}{EXTRA_CSS}</style></head>'
            f'<body><main><h1>{html.escape(title)}</h1>{banner}'
            f'<p class="lede">Each bar is 100% of one group of uploads. A new run adds a bar '
            f'under every slice. Hover a segment for the reasons inside it.</p>'
            f'<div class="legend">{legend}</div>'
            f'<details><summary>How to read this page</summary>'
            f'<p>Every upload ends in exactly one outcome, so each bar adds to 100%. Uploads are '
            f'split into two groups that are never mixed: those that already have a facility on '
            f'the platform (did we find it?) and genuinely new ones (did we leave them alone?).</p>'
            f'{meanings}</details>{"".join(sections)}</main></body></html>')
