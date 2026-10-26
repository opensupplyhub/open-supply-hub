#!/usr/bin/env python3
"""Interactive per-upload outcome page. OSDEV-3277.

Builds one self-contained HTML page from real moderated pairs and one or more
models' scores. Each slice (country) gets ONE bar per run, covering all of its
uploads, split into the six outcomes decided by outcomes.py. Two sliders on the
page change the candidate floor and the auto bar, and every bar is recomputed in
the browser, so you can see what a threshold change would do.

How uploads are rebuilt. The pairs file has no upload id, but every pair from
one upload shares the same cleaned upload text and country, so pairs are grouped
on that. An upload with exactly one confirmed candidate has a true match; one
with none is genuinely new (a moderator rejected every candidate). Uploads with
two or more confirmed candidates are left out: they look like identical text
uploaded more than once, which would blur their candidate lists. The count left
out is printed on the page.

LIMITS, shown on the page too:
  * The population is uploads that reached human review (they have a moderator
    decision), so it is the hard cases. "Correctly matched" means "would have been
    linked automatically at these settings".
  * Only candidates a moderator reviewed are present, so competing candidates
    are undercounted and "several above the bar" is an underestimate.
  * Every candidate counts as retrieved, so "never retrieved" cannot appear.

The rule in the page's JavaScript mirrors outcomes.classify_upload exactly (see
the parity check in the build notes). Pure stdlib. Usage:

  python3 upload_page.py --pairs pairs.csv --scores "baseline=scores.csv" \
      [--scores "other=scores2.csv"] --out page.html [--min-uploads 300]
"""
import argparse
import collections
import csv
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import record  # noqa: E402
from run_history import CSS as BASE_CSS, sha256_of  # noqa: E402
from upload_bars import CAUSE_TEXT, EXTRA_CSS, OUTCOMES  # noqa: E402

# Shown in this order after "All uploads", whatever their size.
PINNED = [("kr", "Korea"), ("cn", "China"), ("mx", "Mexico"), ("bd", "Bangladesh"),
          ("vn", "Vietnam"), ("in", "India")]
SHORT = {"correctly_matched": "Correctly matched", "correctly_new": "Correctly new",
         "review_below_bar": "Review: below bar", "review_above_bar": "Review: several above bar",
         "duplicate": "Duplicate", "incorrect_match": "Incorrect match"}

PAGE_CSS = """
.panel{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
padding:10px 0 12px;margin:0 0 8px}
.panel .row{display:flex;flex-wrap:wrap;gap:10px 28px;align-items:center}
.ctl{display:flex;flex-direction:column;min-width:240px;flex:1}
.ctl label{font-size:13px;color:var(--muted)} .ctl output{font-weight:700;color:var(--fg);margin-left:6px}
.ctl input[type=range]{width:100%}
.presets button,.reset{font:inherit;font-size:13px;padding:4px 10px;margin-right:6px;border:1px solid var(--line);
background:var(--card);color:var(--fg);border-radius:6px;cursor:pointer}
.mix{font-size:12px;color:var(--muted);margin:0 0 3px}
.bar .seg{padding:0 6px;text-overflow:ellipsis}
.delta{color:var(--muted);font-size:11px}
.spread{font-size:12px;color:var(--muted);margin:2px 0 6px;padding:4px 8px;border-left:3px solid var(--line)}
.prov{margin-top:32px;font-size:12px;color:var(--muted)}
"""

JS = r"""
const D = __DATA__;
const OUT = D.outcomes, CAUSE = D.causes;
const DEF = {auto: D.defaults.auto, floor: D.defaults.floor};
const EX = D.uploads.map(u => u[2].split('').map(c => c === '1'));

// BEGIN classify
function classify(scores, exact, trueIdx, floor, auto) {
  const aboveFloor = [];
  for (let i = 0; i < scores.length; i++) if (scores[i] >= floor) aboveFloor.push(i);
  const aboveBar = aboveFloor.filter(i => scores[i] > auto);
  let action = 'review', chosen = -1;
  if (aboveFloor.length === 0) action = 'new';
  else if (aboveFloor.length === 1) {
    if (scores[aboveFloor[0]] >= auto) { action = 'auto'; chosen = aboveFloor[0]; }
  } else if (aboveBar.length === 1) { action = 'auto'; chosen = aboveBar[0]; }
  else if (aboveBar.length > 1) {
    const ex = aboveFloor.filter(i => exact[i]);
    if (ex.length === 1) { action = 'auto'; chosen = ex[0]; }
  }
  const onList = trueIdx >= 0 && scores[trueIdx] >= floor;
  if (action === 'auto') {
    if (trueIdx < 0) return ['incorrect_match', 'no_true_match_exists'];
    if (chosen === trueIdx)
      return ['correctly_matched', (aboveBar.length === 1 || aboveFloor.length === 1) ? 'alone_above_bar' : 'exact_string_tie_break'];
    return ['incorrect_match', onList ? 'true_match_not_chosen' : 'true_match_scored_below_floor'];
  }
  if (action === 'new') {
    if (trueIdx < 0) return ['correctly_new', 'nothing_reached_floor'];
    return ['duplicate', 'scored_below_floor'];
  }
  if (trueIdx >= 0 && !onList) return ['duplicate', 'scored_below_floor'];
  return [aboveBar.length >= 2 ? 'review_above_bar' : 'review_below_bar', 'review'];
}
// END classify

function tally(run, floor, auto) {
  const res = {};
  const get = k => res[k] || (res[k] = {n: 0, counts: {}, causes: {}});
  for (let i = 0; i < D.uploads.length; i++) {
    const u = D.uploads[i];
    const [o, c] = classify(run.scores[i], EX[i], u[1], floor, auto);
    for (const k of ['ALL', D.countries[u[0]]]) {
      const t = get(k);
      t.n++; t.counts[o] = (t.counts[o] || 0) + 1;
      const cc = t.causes[o] || (t.causes[o] = {}); cc[c] = (cc[c] || 0) + 1;
    }
  }
  return res;
}

function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
const pct = (c, n) => n ? c / n * 100 : 0;

function barHtml(t, base, showDelta) {
  if (!t || !t.n) return '<div class="cap">no uploads</div>';
  const segs = [], cap = [], plain = [];
  for (const o of OUT) {
    const c = t.counts[o.key] || 0;
    if (!c) continue;
    const p = pct(c, t.n);
    const causes = t.causes[o.key] || {};
    const why = Object.entries(causes).sort((a, b) => b[1] - a[1])
      .map(([k, v]) => (CAUSE[k] || k) + ' ' + v).join('; ');
    const showWhy = why && !o.key.startsWith('review');
    const label = p >= 17 ? o.short + ' ' + Math.round(p) + '%' : (p >= 6 ? Math.round(p) + '%' : '');
    segs.push('<span class="seg ' + o.css + '" style="width:' + p.toFixed(3) + '%" title="' +
      esc(o.label + ': ' + c + ' (' + p.toFixed(1) + '%)' + (why ? '. ' + why : '')) + '">' + esc(label) + '</span>');
    let d = '';
    if (showDelta && base) {
      const bp = pct((base.counts[o.key] || 0), base.n), diff = p - bp;
      d = ' <span class="delta">(' + (diff >= 0 ? '+' : '') + diff.toFixed(1) + ' pts vs default)</span>';
    }
    cap.push('<b>' + esc(o.short) + '</b> ' + c + ' (' + p.toFixed(1) + '%)' + d +
      (showWhy ? ' <span class="why">[' + esc(why) + ']</span>' : ''));
    plain.push(o.short + ' ' + c + ' (' + p.toFixed(1) + '%)');
  }
  return '<div class="bar" role="img" aria-label="' + esc(plain.join('; ')) + '">' + segs.join('') + '</div>' +
         '<div class="cap">' + cap.join(' &middot; ') + '</div>';
}

let state = {auto: DEF.auto, floor: DEF.floor};
const baseTallies = D.runs.map(r => tally(r, DEF.floor, DEF.auto));

function render() {
  const changed = state.auto !== DEF.auto || state.floor !== DEF.floor;
  const tallies = D.runs.map(r => tally(r, state.floor, state.auto));
  const out = [];
  for (const s of D.show) {
    const mix = D.mix[s.key];
    let rows = '';
    D.runs.forEach((r, i) => {
      rows += '<div class="run"><div class="runlabel"><b>' + esc(r.id) + '</b><span class="meta">' + esc(r.meta) +
        '</span></div><div>' + barHtml(tallies[i][s.key], baseTallies[i][s.key], changed) + '</div></div>';
    });
    let spread = '';
    if (D.runs.length > 1) {
      const parts = [];
      for (const o of OUT) {
        const ps = tallies.map(t => t[s.key] ? pct(t[s.key].counts[o.key] || 0, t[s.key].n) : 0);
        const mx = Math.max(...ps), mn = Math.min(...ps);
        if (mx > 0) parts.push('<b>' + esc(o.short) + '</b> ' + (mx - mn).toFixed(1));
      }
      spread = '<div class="spread">Spread across ' + D.runs.length + ' runs (highest minus lowest, in percentage points): ' +
        parts.join(' &middot; ') + '</div>';
    }
    out.push('<section><h2>' + esc(s.label) + '<small>' + (mix ? mix.n + ' uploads' : '') + '</small></h2>' +
      '<div class="mix">' + (mix ? mix.match + ' have an existing facility, ' + mix.new + ' are genuinely new' : '') + '</div>' + rows + spread + '</section>');
  }
  document.getElementById('bars').innerHTML = out.join('');
  document.getElementById('autoOut').textContent = state.auto.toFixed(2);
  document.getElementById('floorOut').textContent = state.floor.toFixed(2);
  document.getElementById('changed').textContent = changed ? 'Changes vs default are shown next to each count.' : 'At the default thresholds.';
}

function setState(auto, floor, from) {
  auto = Math.round(auto * 100) / 100; floor = Math.round(floor * 100) / 100;
  if (floor > auto) { if (from === 'auto') floor = auto; else auto = floor; }
  state = {auto, floor};
  document.getElementById('auto').value = auto; document.getElementById('floor').value = floor;
  render();
}
if (typeof document !== 'undefined') {
  document.getElementById('auto').addEventListener('input', e => setState(+e.target.value, state.floor, 'auto'));
  document.getElementById('floor').addEventListener('input', e => setState(state.auto, +e.target.value, 'floor'));
  document.querySelectorAll('[data-a]').forEach(b => b.addEventListener('click', () => setState(+b.dataset.a, +b.dataset.f, 'auto')));
  document.getElementById('auto').value = DEF.auto; document.getElementById('floor').value = DEF.floor;
  render();
}
"""


def load_scores(path):
    """Read a scores CSV (match_id, retrained_conf) into {match_id: float}."""
    with open(path, newline="") as f:
        return {r["match_id"]: float(r["retrained_conf"]) for r in csv.DictReader(f)}


def build_data(pairs_path, score_specs, min_uploads, auto, floor):
    """Group pairs into uploads and assemble everything the page needs.

    Returns (data dict for the page, stats dict for the provenance note)."""
    runs_scores = []
    for spec in score_specs:
        name, _, path = spec.partition("=")
        runs_scores.append((name, path, load_scores(path)))
    common = set.intersection(*(set(s) for _, _, s in runs_scores))

    groups = collections.defaultdict(list)
    used = skipped = 0
    with open(pairs_path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            mid = r["match_id"]
            if mid not in common:
                skipped += 1
                continue
            left = record(r["item_clean_name"] or r["item_name"],
                          r["item_clean_address"] or r["item_address"], r["item_country"])
            right = record(r["fac_name"], r["fac_address"], r["fac_country"])
            groups[(left["country"], left["name"], left["address"])].append(
                (int(mid) if mid.isdigit() else mid, mid, r["status"] == "CONFIRMED", left == right))
            used += 1

    uploads, upload_scores = [], [[] for _ in runs_scores]
    ambiguous = 0
    countries = sorted({k[0] for k in groups})
    cidx = {c: i for i, c in enumerate(countries)}
    mix = collections.defaultdict(lambda: {"n": 0, "match": 0, "new": 0})
    for key in sorted(groups):
        cands = sorted(groups[key])
        confirmed = [i for i, c in enumerate(cands) if c[2]]
        if len(confirmed) > 1:
            ambiguous += 1
            continue
        true_idx = confirmed[0] if confirmed else -1
        uploads.append([cidx[key[0]], true_idx, "".join("1" if c[3] else "0" for c in cands)])
        for ri, (_, _, sc) in enumerate(runs_scores):
            upload_scores[ri].append([round(sc[c[1]], 4) for c in cands])
        for k in ("ALL", key[0]):
            m = mix[k]
            m["n"] += 1
            m["match" if true_idx >= 0 else "new"] += 1

    show = [{"key": "ALL", "label": "All uploads"}]
    pinned = {c for c, _ in PINNED}
    show += [{"key": c, "label": f"{n} ({c})"} for c, n in PINNED if c in mix]
    others = sorted((c for c in mix if c != "ALL" and c not in pinned and mix[c]["n"] >= min_uploads),
                    key=lambda c: -mix[c]["n"])
    show += [{"key": c, "label": c.upper()} for c in others]

    data = {
        "outcomes": [{"key": k, "label": lab, "short": SHORT[k], "css": css, "meaning": m}
                     for k, lab, m, css in OUTCOMES],
        "causes": CAUSE_TEXT, "defaults": {"auto": auto, "floor": floor},
        "countries": countries, "show": show, "mix": mix, "uploads": uploads,
        "runs": [{"id": name, "meta": os.path.basename(path), "scores": upload_scores[i]}
                 for i, (name, path, _) in enumerate(runs_scores)],
    }
    stats = {"pairs_used": used, "pairs_without_score": skipped,
             "uploads_usable": len(uploads), "uploads_ambiguous_left_out": ambiguous,
             "with_match": mix["ALL"]["match"], "new": mix["ALL"]["new"]}
    return data, stats


def render_page(data, stats, pairs_path):
    """Wrap the data in the page: controls, legend, caveats, and the script."""
    legend = "".join(f'<span title="{html.escape(o["meaning"])}"><i class="sw {o["css"]}"></i>'
                     f'{html.escape(o["label"])}</span>' for o in data["outcomes"])
    meanings = "".join(f'<p><b>{html.escape(o["label"])}.</b> {html.escape(o["meaning"])}</p>'
                       for o in data["outcomes"])
    d = data["defaults"]
    script = JS.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    caveat = (
        "<b>Real moderated uploads, re-scored by the model.</b> This is the population of uploads that "
        "reached human review, so it is the hard cases, and \"correctly matched\" means \"would have been "
        "linked automatically at these settings\". Only candidates a moderator reviewed are present, so "
        "competing candidates are undercounted and \"several above the bar\" is an underestimate. Every "
        "candidate counts as retrieved, so \"never retrieved\" cannot appear here.")
    prov = (f"Built from {html.escape(os.path.basename(pairs_path))} (sha256 "
            f"{sha256_of(pairs_path)[:12]}): {stats['pairs_used']} pairs grouped into "
            f"{stats['uploads_usable'] + stats['uploads_ambiguous_left_out']} uploads by cleaned text and "
            f"country; {stats['uploads_ambiguous_left_out']} uploads with two or more confirmed candidates "
            f"were left out; {stats['uploads_usable']} are shown ({stats['with_match']} with an existing "
            f"facility, {stats['new']} genuinely new).")
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Upload outcomes by country</title><style>{BASE_CSS}{EXTRA_CSS}{PAGE_CSS}</style></head>'
        f'<body><main><h1>What happens to uploads, one bar per run</h1>'
        f'<div class="banner">{caveat}</div>'
        f'<div class="panel"><div class="row">'
        f'<div class="ctl"><label for="auto">Auto-match bar (at or above links automatically)'
        f'<output id="autoOut"></output></label><input type="range" id="auto" min="0.5" max="1" step="0.01"></div>'
        f'<div class="ctl"><label for="floor">Candidate floor (below this a candidate is not offered)'
        f'<output id="floorOut"></output></label><input type="range" id="floor" min="0" max="0.99" step="0.01"></div>'
        f'<div class="presets"><button data-a="{d["auto"]}" data-f="{d["floor"]}">Production now '
        f'({d["auto"]:.2f} / {d["floor"]:.2f})</button><button data-a="0.8" data-f="0.3">Retrain branch (0.80 / 0.30)</button>'
        f'<button data-a="0.75" data-f="0.3">0.75 / 0.30</button></div></div>'
        f'<div class="note" id="changed"></div></div>'
        f'<div class="legend">{legend}</div>'
        f'<details><summary>How to read this page</summary>'
        f'<p>Each bar is 100% of one slice\'s uploads. Every upload ends in exactly one outcome. Move the '
        f'sliders to see how the outcomes would change; the numbers beside each count show the change from '
        f'the default settings.</p>{meanings}</details>'
        f'<div id="bars"></div><p class="prov">{prov}</p></main><script>{script}</script></body></html>')


def main():
    """Build the interactive page from the pairs file and one or more score files."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True)
    p.add_argument("--scores", action="append", required=True, metavar="NAME=PATH")
    p.add_argument("--out", required=True)
    p.add_argument("--min-uploads", type=int, default=300,
                   help="also show other countries with at least this many uploads")
    p.add_argument("--auto", type=float, default=0.8)
    p.add_argument("--floor", type=float, default=0.5)
    args = p.parse_args()
    data, stats = build_data(args.pairs, args.scores, args.min_uploads, args.auto, args.floor)
    page = render_page(data, stats, args.pairs)
    with open(args.out, "w") as f:
        f.write(page)
    print(f"wrote {args.out} ({len(page) / 1e6:.1f} MB)")
    print(stats)


if __name__ == "__main__":
    main()
