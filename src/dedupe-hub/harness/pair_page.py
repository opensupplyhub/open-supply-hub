#!/usr/bin/env python3
"""Interactive pair-level outcome page. OSDEV-3277.

One self-contained HTML page over the frozen evaluation pairs. For every slice
(country, plus the lookalike class) and every run there is ONE bar whose 100% is
the slice's CONFIRMED matches, the pairs a human approved. Each confirmed match
ends in one of four places:

  never considered         the search rules would not even have compared the two
                           records (needs the retrieval check)
  scored too low           retrieved, but scored below the candidate floor
  human review             retrieved, scored between the floor and the auto bar
  auto-matched correctly   retrieved and scored at or above the auto bar

Wrong matches cannot live in that bar, because they come from REJECTED pairs the
model would have accepted. They are shown beside the bar: of everything
auto-accepted, how many were wrong. So is the review workload, which counts both
matches and non-matches. A toggle chooses whether sibling-pick rejections count
as non-matches (all labels) or are dropped (clean).

Two sliders set the candidate floor and the auto bar, and every bar is recomputed
in the browser. With several runs, a line under each slice gives the spread
across runs.

Each pair is judged on its own, so competing candidates for the same upload are
ignored; the per-upload page (upload_page.py) accounts for them. Retrieval comes
from verify_retrain.py --retrieval-out, which indexes only the evaluation
facilities, so absolute rates depend on that index size.

Usage:
  python3 pair_page.py --pairs pairs.csv --eval-set eval_set.csv \
      --scores "seed_42=scores.csv" --retrieval "seed_42=retrieval.csv" \
      [--scores ...] [--retrieval ...] --out page.html [--min-pairs 300]
"""
import argparse
import csv
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evaluate import load_pairs  # noqa: E402
from run_history import CSS as BASE_CSS, sha256_of  # noqa: E402
from slice_report import load_eval_set  # noqa: E402
from slices import is_lookalike  # noqa: E402
from upload_bars import EXTRA_CSS  # noqa: E402
from upload_page import PAGE_CSS, PINNED  # noqa: E402

SEGMENTS = [
    {"key": "never", "label": "Never considered", "css": "never",
     "meaning": "The search rules would not have compared the two records at all, so the "
                "match is lost and a duplicate gets created."},
    {"key": "low", "label": "Scored too low", "css": "low",
     "meaning": "Retrieved, but the score is below the candidate floor, so it is not offered "
                "and a duplicate gets created."},
    {"key": "review", "label": "Human review", "css": "review",
     "meaning": "Retrieved and scored between the floor and the auto bar: a person decides."},
    {"key": "ok", "label": "Auto-matched correctly", "css": "correct",
     "meaning": "Retrieved and scored at or above the auto bar: linked automatically, correctly."},
]

LOOK_KEY, LOOK_LABEL = "LOOK", "Lookalike class (near-identical siblings)"

JS = r"""
const D = __DATA__;
const SEG = D.segments;
const DEF = {auto: D.defaults.auto, floor: D.defaults.floor};

function tally(run, floor, auto, clean) {
  const res = {};
  const get = k => res[k] || (res[k] = {n: 0, never: 0, low: 0, review: 0, ok: 0, wrong: 0, reviewNeg: 0, accepted: 0});
  for (let i = 0; i < D.pairs.length; i++) {
    const p = D.pairs[i];
    const keys = ['ALL', D.countries[p[0]]];
    if (p[2] & 4) keys.push('LOOK');
    const ret = run.ret.charCodeAt(i) === 49;
    const s = run.scores[i];
    if (p[1] === 1) {
      let o;
      if (!ret) o = 'never'; else if (s < floor) o = 'low'; else if (s < auto) o = 'review'; else o = 'ok';
      for (const k of keys) { const t = get(k); t.n++; t[o]++; if (o === 'ok') t.accepted++; }
    } else {
      if (clean && (p[2] & 1)) continue;
      if (ret && s >= auto) { for (const k of keys) { const t = get(k); t.wrong++; t.accepted++; } }
      else if (ret && s >= floor) { for (const k of keys) get(k).reviewNeg++; }
    }
  }
  return res;
}

function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
const pct = (c, n) => n ? c / n * 100 : 0;

function barHtml(t, base, showDelta) {
  if (!t || !t.n) return '<div class="cap">no confirmed matches in this slice</div>';
  const segs = [], cap = [], plain = [];
  for (const o of SEG) {
    const c = t[o.key];
    if (!c) continue;
    const p = pct(c, t.n);
    const label = p >= 17 ? o.label + ' ' + Math.round(p) + '%' : (p >= 6 ? Math.round(p) + '%' : '');
    segs.push('<span class="seg ' + o.css + '" style="width:' + p.toFixed(3) + '%" title="' +
      esc(o.label + ': ' + c + ' (' + p.toFixed(1) + '%). ' + o.meaning) + '">' + esc(label) + '</span>');
    let d = '';
    if (showDelta && base && base.n) {
      const diff = p - pct(base[o.key], base.n);
      d = ' <span class="delta">(' + (diff >= 0 ? '+' : '') + diff.toFixed(1) + ' pts vs default)</span>';
    }
    cap.push('<b>' + esc(o.label) + '</b> ' + c + ' (' + p.toFixed(1) + '%)' + d);
    plain.push(o.label + ' ' + c + ' (' + p.toFixed(1) + '%)');
  }
  const wrongShare = t.accepted ? pct(t.wrong, t.accepted) : 0;
  let wd = '';
  if (showDelta && base && base.accepted) {
    const diff = wrongShare - pct(base.wrong, base.accepted);
    wd = ' <span class="delta">(' + (diff >= 0 ? '+' : '') + diff.toFixed(1) + ' pts vs default)</span>';
  }
  const side = '<div class="side"><b>Wrongly auto-accepted:</b> ' + t.wrong + ' of ' + t.accepted +
    ' auto-accepted pairs (' + wrongShare.toFixed(1) + '%)' + wd + ' &nbsp;|&nbsp; <b>Reaching a human:</b> ' +
    (t.review + t.reviewNeg) + ' pairs (' + t.review + ' matches + ' + t.reviewNeg + ' non-matches)</div>';
  return '<div class="bar" role="img" aria-label="' + esc(plain.join('; ')) + '">' + segs.join('') + '</div>' +
         '<div class="cap">' + cap.join(' &middot; ') + '</div>' + side;
}

let state = {auto: DEF.auto, floor: DEF.floor, clean: false};
const base = {};
function baseTallies(clean) {
  const k = clean ? 'c' : 'a';
  return base[k] || (base[k] = D.runs.map(r => tally(r, DEF.floor, DEF.auto, clean)));
}

function render() {
  const changed = state.auto !== DEF.auto || state.floor !== DEF.floor;
  const tallies = D.runs.map(r => tally(r, state.floor, state.auto, state.clean));
  const bt = baseTallies(state.clean);
  const out = [];
  for (const s of D.show) {
    const mix = D.mix[s.key];
    let rows = '';
    D.runs.forEach((r, i) => {
      rows += '<div class="run"><div class="runlabel"><b>' + esc(r.id) + '</b><span class="meta">' + esc(r.meta) +
        '</span></div><div>' + barHtml(tallies[i][s.key], bt[i][s.key], changed) + '</div></div>';
    });
    let spread = '';
    if (D.runs.length > 1) {
      const parts = [];
      for (const o of SEG) {
        const ps = tallies.map(t => t[s.key] ? pct(t[s.key][o.key], t[s.key].n) : 0);
        if (Math.max(...ps) > 0) parts.push('<b>' + esc(o.label) + '</b> ' + (Math.max(...ps) - Math.min(...ps)).toFixed(1));
      }
      spread = '<div class="spread">Spread across ' + D.runs.length + ' runs (highest minus lowest, in percentage points): ' +
        parts.join(' &middot; ') + '</div>';
    }
    out.push('<section><h2>' + esc(s.label) + '<small>' + (mix ? mix.confirmed + ' confirmed matches' : '') + '</small></h2>' +
      '<div class="mix">' + (mix ? mix.rejected + ' rejected pairs also in this slice' : '') + '</div>' + rows + spread + '</section>');
  }
  document.getElementById('bars').innerHTML = out.join('');
  document.getElementById('autoOut').textContent = state.auto.toFixed(2);
  document.getElementById('floorOut').textContent = state.floor.toFixed(2);
  document.getElementById('changed').textContent = changed ? 'Changes vs default are shown next to each count.' : 'At the default thresholds.';
}

function setState(auto, floor, from) {
  auto = Math.round(auto * 100) / 100; floor = Math.round(floor * 100) / 100;
  if (floor > auto) { if (from === 'auto') floor = auto; else auto = floor; }
  state.auto = auto; state.floor = floor;
  document.getElementById('auto').value = auto; document.getElementById('floor').value = floor;
  render();
}
function setClean(clean) { state.clean = clean; render(); }

if (typeof document !== 'undefined') {
  document.getElementById('auto').addEventListener('input', e => setState(+e.target.value, state.floor, 'auto'));
  document.getElementById('floor').addEventListener('input', e => setState(state.auto, +e.target.value, 'floor'));
  document.querySelectorAll('[data-a]').forEach(b => b.addEventListener('click', () => setState(+b.dataset.a, +b.dataset.f, 'auto')));
  document.querySelectorAll('input[name=labels]').forEach(r => r.addEventListener('change', e => setClean(e.target.value === 'clean')));
  document.getElementById('auto').value = DEF.auto; document.getElementById('floor').value = DEF.floor;
  render();
}
"""

EXTRA_PAGE_CSS = """
.side{font-size:13px;margin:4px 0 4px;padding:4px 8px;background:var(--card);border-radius:4px}
.labels{font-size:13px;margin-top:6px} .labels label{margin-right:14px}
"""


def read_flags(path, ids, name):
    """Read a retrieval CSV (match_id, retrieved, score) into {match_id: bool} and
    insist that it covers every evaluation pair, since a partial file cannot be
    turned into percentages."""
    got = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            got[r["match_id"]] = r["retrieved"] == "1"
    missing = [m for m in ids if m not in got]
    if missing:
        sys.exit(f"retrieval file for {name} is missing {len(missing)} of the {len(ids)} "
                 "evaluation pairs. Re-run verify_retrain.py without --retrieval-limit.")
    return got


def build_data(pairs_path, eval_path, score_specs, retrieval_specs, min_pairs, auto, floor):
    """Assemble the page's data: one entry per evaluation pair, and per run its
    scores and retrieval flags. Returns (data, stats)."""
    tags, manifest = load_eval_set(eval_path, pairs_path)
    rows = [r for r in load_pairs(pairs_path) if r["match_id"] in tags]
    rows.sort(key=lambda r: (len(r["match_id"]), r["match_id"]))
    if len(rows) != manifest["eval_rows"]:
        sys.exit(f"Only {len(rows)} of the {manifest['eval_rows']} frozen pairs are in {pairs_path}.")
    ids = [r["match_id"] for r in rows]
    retrievals = dict(spec.partition("=")[::2] for spec in retrieval_specs)

    runs = []
    for spec in score_specs:
        name, _, path = spec.partition("=")
        with open(path, newline="") as f:
            sc = {r["match_id"]: float(r["retrained_conf"]) for r in csv.DictReader(f)}
        missing = [m for m in ids if m not in sc]
        if missing:
            sys.exit(f"{name}: no score for {len(missing)} of the {len(ids)} frozen evaluation pairs.")
        flags = read_flags(retrievals[name], ids, name) if name in retrievals else None
        runs.append({"id": name,
                     "meta": os.path.basename(path) + ("" if flags else " (no retrieval check)"),
                     "scores": [round(sc[m], 4) for m in ids],
                     "ret": "".join("1" if (flags is None or flags[m]) else "0" for m in ids)})

    countries = sorted({r["country"] for r in rows})
    cidx = {c: i for i, c in enumerate(countries)}
    pairs, mix = [], {}
    for r in rows:
        t = tags[r["match_id"]]
        flag = (1 if t["pick_one"] else 0) | (2 if t["exact"] else 0) | (4 if is_lookalike(r) else 0)
        pairs.append([cidx[r["country"]], r["label"], flag])
        keys = ["ALL", r["country"]] + ([LOOK_KEY] if flag & 4 else [])
        for k in keys:
            m = mix.setdefault(k, {"confirmed": 0, "rejected": 0})
            m["confirmed" if r["label"] == 1 else "rejected"] += 1

    pinned = {c for c, _ in PINNED}
    show = [{"key": "ALL", "label": "All evaluation pairs"}]
    show += [{"key": c, "label": f"{n} ({c})"} for c, n in PINNED if c in mix]
    show.append({"key": LOOK_KEY, "label": LOOK_LABEL})
    others = sorted((c for c in mix if c not in pinned and c not in ("ALL", LOOK_KEY)
                     and mix[c]["confirmed"] >= min_pairs), key=lambda c: -mix[c]["confirmed"])
    show += [{"key": c, "label": c.upper()} for c in others]

    data = {"segments": SEGMENTS, "defaults": {"auto": auto, "floor": floor},
            "countries": countries, "show": show, "mix": mix, "pairs": pairs, "runs": runs}
    stats = {"pairs": len(rows), "confirmed": mix["ALL"]["confirmed"], "rejected": mix["ALL"]["rejected"],
             "eval_sha": manifest["eval_set_sha256"][:12], "pairs_sha": sha256_of(pairs_path)[:12]}
    return data, stats


def render_page(data, stats):
    """Wrap the data in the page: controls, legend, caveats and the script."""
    legend = "".join(f'<span title="{html.escape(s["meaning"])}"><i class="sw {s["css"]}"></i>'
                     f'{html.escape(s["label"])}</span>' for s in data["segments"])
    meanings = "".join(f'<p><b>{html.escape(s["label"])}.</b> {html.escape(s["meaning"])}</p>'
                       for s in data["segments"])
    d = data["defaults"]
    script = JS.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    caveat = ("<b>Pair level.</b> Each human-approved pair is judged on its own, so competing candidates for "
              "the same upload are ignored. Wrongly auto-accepted counts every rejected pair above the bar, "
              "even when production would have sent several above-bar candidates to review, so it "
              "overstates real wrong merges. The never-considered piece comes from a retrieval check that "
              "indexes only the evaluation facilities, so its absolute level depends on that index size.")
    prov = (f"Frozen evaluation set {html.escape(stats['eval_sha'])} (pairs file {html.escape(stats['pairs_sha'])}): "
            f"{stats['pairs']} pairs, {stats['confirmed']} confirmed matches and {stats['rejected']} rejected pairs.")
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Match outcomes by country</title><style>{BASE_CSS}{EXTRA_CSS}{PAGE_CSS}{EXTRA_PAGE_CSS}</style></head>'
        f'<body><main><h1>What happens to confirmed matches, one bar per run</h1>'
        f'<div class="banner">{caveat}</div>'
        f'<div class="panel"><div class="row">'
        f'<div class="ctl"><label for="auto">Auto-match bar (at or above links automatically)'
        f'<output id="autoOut"></output></label><input type="range" id="auto" min="0.5" max="1" step="0.01"></div>'
        f'<div class="ctl"><label for="floor">Candidate floor (below this a candidate is not offered)'
        f'<output id="floorOut"></output></label><input type="range" id="floor" min="0" max="0.99" step="0.01"></div>'
        f'<div class="presets"><button data-a="{d["auto"]}" data-f="{d["floor"]}">Production now '
        f'({d["auto"]:.2f} / {d["floor"]:.2f})</button><button data-a="0.8" data-f="0.3">Retrain branch (0.80 / 0.30)</button>'
        f'<button data-a="0.75" data-f="0.3">0.75 / 0.30</button></div></div>'
        f'<div class="labels">Rejected pairs counted as non-matches: '
        f'<label><input type="radio" name="labels" value="all" checked> all (conservative)</label>'
        f'<label><input type="radio" name="labels" value="clean"> without sibling picks (clean)</label></div>'
        f'<div class="note" id="changed"></div></div>'
        f'<div class="legend">{legend}</div>'
        f'<details><summary>How to read this page</summary>'
        f'<p>Each bar is 100% of one slice\'s confirmed matches, the pairs a human approved. Each ends in '
        f'exactly one of four places. Wrong matches come from rejected pairs, so they are shown beside the bar. '
        f'Move the sliders to see how outcomes would change.</p>{meanings}</details>'
        f'<div id="bars"></div><p class="prov">{prov}</p></main><script>{script}</script></body></html>')


def main():
    """Build the interactive pair-level page from the frozen set, scores and retrieval checks."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True)
    p.add_argument("--eval-set", required=True)
    p.add_argument("--scores", action="append", required=True, metavar="NAME=PATH")
    p.add_argument("--retrieval", action="append", default=[], metavar="NAME=PATH")
    p.add_argument("--out", required=True)
    p.add_argument("--min-pairs", type=int, default=300,
                   help="also show other countries with at least this many confirmed matches")
    p.add_argument("--auto", type=float, default=0.8)
    p.add_argument("--floor", type=float, default=0.5)
    args = p.parse_args()
    data, stats = build_data(args.pairs, args.eval_set, args.scores, args.retrieval,
                             args.min_pairs, args.auto, args.floor)
    page = render_page(data, stats)
    with open(args.out, "w") as f:
        f.write(page)
    print(f"wrote {args.out} ({len(page) / 1e6:.1f} MB)")
    print(stats)


if __name__ == "__main__":
    main()
