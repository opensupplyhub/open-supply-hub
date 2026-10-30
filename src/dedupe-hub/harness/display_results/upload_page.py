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
  * Without a --retrieval file for a run, every candidate counts as retrieved, so
    "never retrieved" cannot appear. With one, a true match the search rules did
    not return becomes a Duplicate.

The rule in the page's JavaScript mirrors outcomes.classify_upload exactly (see
the parity check in the build notes). Pure stdlib. Usage:

  python3 display_results/upload_page.py --pairs pairs.csv --scores "baseline=scores.csv" \
      [--scores "other=scores2.csv"] [--retrieval "baseline=retrieval.csv"] --out page.html [--min-uploads 300]
"""
import argparse
import collections
import csv
import html
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
from make_training_json import record  # noqa: E402
from run_history import CSS as BASE_CSS, sha256_of  # noqa: E402
from slices import is_lookalike  # noqa: E402
from upload_bars import CAUSE_TEXT as BASE_CAUSE_TEXT, EXTRA_CSS, OUTCOMES as BASE_OUTCOMES  # noqa: E402

# This page splits Duplicate by whether the search rules ever compared the true match,
# so there are seven bar segments. outcomes.classify_upload still returns six outcomes;
# the split is its "never_retrieved" cause.
OUTCOMES = []
for _k, _lab, _m, _css in BASE_OUTCOMES:
    if _k == "duplicate":
        OUTCOMES.append(("duplicate_compared", "Duplicate: compared but not matched",
                         "The true match was retrieved and scored, but the score fell below the floor, "
                         "so a new facility is created (or a person is shown candidates without it).", "o-dup"))
        OUTCOMES.append(("duplicate_never", "Duplicate: never compared",
                         "The search rules never returned the true match, so it was never scored and "
                         "a duplicate is created. Needs the retrieval check.", "o-dupnever"))
    else:
        OUTCOMES.append((_k, _lab, _m, _css))
CAUSE_TEXT = dict(BASE_CAUSE_TEXT,
                  new_created="nothing reached the floor, so a new facility was created",
                  nothing_retrieved="the search returned nothing",
                  nothing_reached_floor="candidates were scored and all fell below the floor",
                  review_missing="went to a person without the right facility on the list, so it cannot be picked")

# Shown in this order after "All uploads", whatever their size.
PINNED = [("kr", "Korea"), ("cn", "China"), ("mx", "Mexico"), ("bd", "Bangladesh"),
          ("vn", "Vietnam"), ("in", "India")]
SHORT = {"correctly_matched": "Correctly matched", "correctly_new": "Correctly new",
         "review_below_bar": "Review: below bar", "review_above_bar": "Review: several above bar",
         "duplicate_compared": "Duplicate: compared", "duplicate_never": "Duplicate: never compared",
         "incorrect_match": "Incorrect match"}

PAGE_CSS = """
.o-dupnever{background:#8b4a9c;color:#fff}
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
.reg{border:1px solid var(--line);border-radius:6px;padding:8px 12px;margin:8px 0;font-size:13px}
.reg label{margin-right:12px} .reg input[type=number]{width:60px} .reg select{font:inherit;font-size:13px}
#matrix{max-height:60vh;overflow:auto}
h3.grp{margin:28px 0 4px;padding-top:10px;border-top:2px solid var(--line);font-size:16px}
table.matrix,table.band{border-collapse:collapse;font-size:12px;margin:6px 0}
table.matrix th,table.matrix td,table.band th,table.band td{border:1px solid var(--line);padding:3px 8px;text-align:left}
table.matrix td.regress{background:#f8d7da;color:#58151c} table.matrix td.improve{background:#d1e7dd;color:#0a3622}
table.matrix td.inc{background:#e9ecef;color:#495057}
@media (prefers-color-scheme:dark){table.matrix td.regress{background:#58151c;color:#f8d7da}
table.matrix td.improve{background:#0a3622;color:#d1e7dd} table.matrix td.inc{background:#343a40;color:#ced4da}}
.thr{white-space:nowrap;font-size:11px} .thr input{width:64px;vertical-align:middle} .thr.ovr{outline:2px solid #2f81f7} .thr.inh{outline:1px dashed #2f81f7}
.thr button{font:inherit;font-size:11px;padding:0 6px}
.sw{display:inline-block;width:10px;height:10px;margin-right:5px;border-radius:2px}
"""

JS = r"""
const D = __DATA__;
const OUT = D.outcomes, CAUSE = D.causes;
const DEF = {auto: D.defaults.auto, floor: D.defaults.floor};
const EX = D.uploads.map(u => u[2].split('').map(c => c === '1'));
for (const r of D.runs) if (r.ret) r.ret = r.ret.map(x => x.split('').map(c => c === '1'));

// BEGIN classify
// `rule` ({promote, hold}) is the optional margin rule; see outcomes.decide for what the two numbers do.
function classify(scores, exact, trueIdx, floor, auto, ret, rule) {
  const got = i => ret ? ret[i] : true;      // retrieved? (missing flags mean every candidate was)
  scores = scores.map((x, i) => got(i) ? x : -1);
  const dup = () => (trueIdx >= 0 && !got(trueIdx)) ? 'duplicate_never' : 'duplicate_compared';
  const why = () => (trueIdx >= 0 && !got(trueIdx)) ? 'never_retrieved' : 'scored_below_floor';
  const aboveFloor = [];
  for (let i = 0; i < scores.length; i++) if (scores[i] >= floor) aboveFloor.push(i);
  const aboveBar = aboveFloor.filter(i => scores[i] > auto);
  let action = 'review', chosen = -1, lead = 0, top = -1;
  if (aboveFloor.length > 1) {                 // how far the best candidate is ahead of the next
    const ranked = aboveFloor.slice().sort((x, y) => scores[y] - scores[x]);
    top = ranked[0]; lead = scores[ranked[0]] - scores[ranked[1]];
  }
  const promote = rule && rule.promote || 0, hold = rule && rule.hold || 0;
  if (aboveFloor.length === 0) action = 'new';
  else if (aboveFloor.length === 1) {
    if (scores[aboveFloor[0]] >= auto) { action = 'auto'; chosen = aboveFloor[0]; }
  } else if (aboveBar.length === 1) {
    if (!(hold && lead < hold)) { action = 'auto'; chosen = aboveBar[0]; }
  } else if (aboveBar.length > 1) {
    if (promote && lead >= promote) { action = 'auto'; chosen = top; }
    else {
      const ex = aboveFloor.filter(i => exact[i]);
      if (ex.length === 1) { action = 'auto'; chosen = ex[0]; }
    }
  }
  const onList = trueIdx >= 0 && scores[trueIdx] >= floor;
  if (action === 'auto') {
    if (trueIdx < 0) return ['incorrect_match', 'no_true_match_exists'];
    if (chosen === trueIdx)
      return ['correctly_matched', (aboveBar.length === 1 || aboveFloor.length === 1) ? 'alone_above_bar'
        : (promote && lead >= promote && !aboveBar.some(i => exact[i])) ? 'margin_win' : 'exact_string_tie_break'];
    return ['incorrect_match', onList ? 'true_match_not_chosen' : 'true_match_' + why()];
  }
  if (action === 'new') {
    if (trueIdx < 0) return ['correctly_new', (ret && !ret.some(Boolean)) ? 'nothing_retrieved' : 'nothing_reached_floor'];
    return [dup(), 'new_created'];
  }
  if (trueIdx >= 0 && !onList) return [dup(), 'review_missing'];
  return [aboveBar.length >= 2 ? 'review_above_bar' : 'review_below_bar', 'review'];
}
// END classify

// `ovr` ({country code: {auto, floor}}) gives some countries their own thresholds; every other
// country uses `floor` and `auto`.
function tally(run, floor, auto, clean, ovr, rule, excl) {
  const res = {};
  const get = k => res[k] || (res[k] = {n: 0, counts: {}, causes: {}});
  for (let i = 0; i < D.uploads.length; i++) {
    const u = D.uploads[i];
    // Clean view: a rejected sibling pick is dropped, as if it had never been a candidate.
    let sc = run.scores[i];
    if (clean && u[3].indexOf('1') >= 0) sc = sc.map((x, j) => u[3][j] === '1' ? -1 : x);
    let fl = floor, au = auto;
    if (ovr) {   // a country's own setting wins over its region's
      const cc = D.countries[u[0]], ov = ovr[cc] || (D.regionOf && ovr[D.regionOf[cc]]);
      if (ov) { fl = ov.floor; au = ov.auto; }
    }
    const [o, c] = classify(sc, EX[i], u[1], fl, au, run.ret ? run.ret[i] : null, rule);
    const inAll = !(excl && excl[D.countries[u[0]]]);   // a country ticked off stays in its own row but leaves the overall rows
    const keys = inAll ? ['ALL', D.countries[u[0]]] : [D.countries[u[0]]];
    if (u[4]) { if (inAll) keys.push('LOOK'); keys.push('LOOK:' + D.countries[u[0]]); }
    const rk = D.regionOf && D.regionOf[D.countries[u[0]]];
    if (rk) keys.push(rk);
    for (const k of keys) {
      const t = get(k);
      t.n++; t.counts[o] = (t.counts[o] || 0) + 1;
      const cc = t.causes[o] || (t.causes[o] = {}); cc[c] = (cc[c] || 0) + 1;
    }
  }
  return state.weighted ? reweight(res, excl) : res;
}

// The overall row, re-weighted: each country counts in proportion to its production volume (D.weightSets, list items) instead of
// its number of uploads here. A country's counts are scaled by weight / uploads, so the shares are the weighted average of the
// countries' shares and the counts read as list items. Countries without a weight, and ones ticked off, are left out.
function reweight(res, excl) {
  const ws = D.weightSets && D.weightSets[state.wset], W = ws && ws.weights;
  if (!W || !res.ALL) return res;
  const out = {n: 0, counts: {}, causes: {}};
  for (const cc of D.countries) {
    const w = W[cc], t = res[cc];
    if (!w || !t || !t.n || (excl && excl[cc])) continue;
    const f = w / t.n;
    for (const [k, v] of Object.entries(t.counts)) out.counts[k] = (out.counts[k] || 0) + v * f;
    for (const [k, cs] of Object.entries(t.causes)) { const c2 = out.causes[k] || (out.causes[k] = {}); for (const [kk, v] of Object.entries(cs)) c2[kk] = (c2[kk] || 0) + v * f; }
  }
  for (const k of Object.keys(out.counts)) { out.counts[k] = Math.round(out.counts[k]); out.n += out.counts[k]; }
  for (const cs of Object.values(out.causes)) for (const kk of Object.keys(cs)) cs[kk] = Math.round(cs[kk]);
  res.ALL = out;
  return res;
}

function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
const pct = (c, n) => n ? c / n * 100 : 0;

const RULES = [
  {key: 'dup', label: 'Duplicates', outs: ['duplicate_compared', 'duplicate_never']},
  {key: 'wrong', label: 'Incorrect matches', outs: ['incorrect_match']},
  {key: 'review', label: 'Human review', outs: ['review_below_bar', 'review_above_bar']},
];
const GROUPS = [...new Set(D.runs.map(r => r.group || 'baseline'))];
const CHALS = GROUPS.filter(g => g !== 'baseline');   // every non-baseline group can be compared
const CHAL = CHALS[0];
const share = (t, outs) => t ? 100 * outs.reduce((a, o) => a + (t.counts[o] || 0), 0) / t.n : 0;
const pick = (vals, how) => how === 'min' ? Math.min(...vals) : how === 'max' ? Math.max(...vals) :
  vals.reduce((a, b) => a + b, 0) / vals.length;
const groupIdx = g => D.runs.map((r, i) => (r.group || 'baseline') === g ? i : -1).filter(i => i >= 0);

// BEGIN verdict
// Lower is better for every rule. Two independent tests, each comparing one baseline number
// with one challenger number: the regression test says "regress" when the challenger's value
// is above the baseline's reference by more than the margin; the improvement test says
// "improve" when it is below by more than the margin. A pairing is {ref, val}: ref picks the
// baseline's reference (worst = its highest share, best = its lowest, or the average) and val
// picks the challenger's (best = lowest, worst = highest, or the average).
const stat = (vals, which, goodIsLow) => pick(vals, which === 'mean' ? 'mean' : (which === 'worst') === goodIsLow ? 'max' : 'min');
function verdict(baseVals, chalVals, reg, imp, margin) {
  const gap = p => stat(chalVals, p.val, true) - stat(baseVals, p.ref, true);
  const r = gap(reg), i = gap(imp);
  const status = r > margin ? 'regress' : i < -margin ? 'improve' : 'same';
  const shown = status === 'improve' ? imp : reg;
  return {b: stat(baseVals, shown.ref, true), c: stat(chalVals, shown.val, true),
          diff: status === 'improve' ? i : r, status};
}
// END verdict

// BEGIN noise
// Noise-based test: the gap between the two averages is measured in units of its standard error,
// the combined run-to-run wobble of the two averages. It counts as a change when it is larger than
// `k` of those units AND larger than `margin` points, the smallest gap worth caring about.
function noiseVerdict(baseVals, chalVals, k, margin) {
  const avg = a => a.reduce((x, y) => x + y, 0) / a.length;
  const variance = a => a.length > 1 ? a.reduce((t, x) => t + (x - avg(a)) ** 2, 0) / (a.length - 1) : 0;
  const diff = avg(chalVals) - avg(baseVals);
  const se = Math.sqrt(variance(baseVals) / baseVals.length + variance(chalVals) / chalVals.length);
  const big = Math.abs(diff) > Math.max(k * se, margin) && Math.abs(diff) > 1e-9;
  return {b: avg(baseVals), c: avg(chalVals), diff, se, status: !big ? 'same' : diff > 0 ? 'regress' : 'improve'};
}
// END noise

// The cell holding a country's own challenger sliders. The All row says the top sliders are the
// default; lookalike rows follow their country.
function thrCell(s, g0) {
  if (s.key === 'ALL') return '<td class="thr">default for every country: the sliders at the top</td>';
  if (s.group !== 'country' && s.group !== 'region') return '<td class="thr">follows its country</td>';
  const own = state.ovr[s.key];
  const parent = s.group === 'country' && D.regionOf ? state.ovr[D.regionOf[s.key]] : null;   // a country inherits its region's setting
  const o = own || parent, a = o ? o.auto : g0.auto, f = o ? o.floor : g0.floor, cc = esc(s.key);
  return '<td class="thr' + (own ? ' ovr' : parent ? ' inh' : '') + '" title="' + (own ? 'its own thresholds' : parent ? 'inherited from its region' : 'the default thresholds') + '">' +
    'bar <input type="range" min="0" max="1" step="0.01" value="' + a + '" data-cc="' + cc + '" data-w="auto">' +
    '<output>' + a.toFixed(2) + '</output> floor <input type="range" min="0" max="0.99" step="0.01" value="' + f + '" data-cc="' + cc + '" data-w="floor">' +
    '<output>' + f.toFixed(2) + '</output> <button data-cc="' + cc + '" data-w="reset" title="Use the default thresholds here">reset</button></td>';
}

// How many countries are ticked off, and the heading text for an overall section.
const nExcl = () => Object.keys(state.excl).length;
function allNote(s, tallies) {
  const wnote = state.weighted && s.key === 'ALL' ? ' [weighted by ' + (D.weightSets && D.weightSets[state.wset] ? D.weightSets[state.wset].label : 'production volume') + '; counts are list items]' : '';
  if (!nExcl() || (s.key !== 'ALL' && s.key !== 'LOOK')) return wnote;
  const t = tallies[0][s.key];
  return ' (' + nExcl() + ' countr' + (nExcl() === 1 ? 'y' : 'ies') + ' left out' + (t && !(state.weighted && s.key === 'ALL') ? '; ' + t.n + ' uploads left' : '') + ')' + wnote;
}

// The verdict for one slice: its own rule if it has one, else the page-wide setting.
function verdictFor(key, bv, cv) {
  const rs = RULESETS[state.ruleBy[key]];
  if (rs) return rs.reg ? verdict(bv, cv, rs.reg, rs.imp, state.margin) : noiseVerdict(bv, cv, state.k, state.margin);
  return state.mode === 'noise' ? noiseVerdict(bv, cv, state.k, state.margin) : verdict(bv, cv, state.reg, state.imp, state.margin);
}
const ruleOptions = sel => '<option value=""' + (sel ? '' : ' selected') + '>page setting</option>' +
  Object.entries(RULESETS).map(([k, r]) => '<option value="' + k + '"' + (sel === k ? ' selected' : '') + '>' + r.label + '</option>').join('');
function ruleCell(s) {
  if (s.group !== 'all' && s.group !== 'region' && s.group !== 'country') return '<td class="thr">follows its country</td>';
  return '<td class="thr"><select data-rule="' + esc(s.key) + '" title="How to judge this slice">' + ruleOptions(state.ruleBy[s.key]) + '</select></td>';
}

function matrixHtml(tallies) {
  if (!CHALS.length) return '';
  const bi = groupIdx('baseline'), ci = groupIdx(state.chal);
  const on = RULES.filter(r => state.rules[r.key]);
  const counts = {regress: 0, improve: 0, same: 0, inconclusive: 0};
  const g0 = state.thr[state.chal] || {auto: state.auto, floor: state.floor};
  let h = '<div class="spread">The tick box beside each country counts it in the <b>All uploads</b> rows. <button data-incl-all="1">tick all</button> <button data-incl-all="0">untick all</button> &nbsp; Rule for every slice: <select data-rule-all="1"><option value="">(choose)</option>' + ruleOptions('').replace(' selected', '') + '</select></div>' +
    '<table class="matrix"><tr><th>Slice</th>' + on.map(r => '<th>' + esc(r.label) + '</th>').join('') +
    '<th>Rule for this slice</th><th>Challenger thresholds for this country</th></tr>';
  let lastGroup = null;
  for (const s of D.show) {
    if (!tallies[bi[0]][s.key]) continue;
    if (s.group !== lastGroup) { lastGroup = s.group; h += '<tr><th colspan="' + (on.length + 3) + '">' + esc(GROUP_TITLE[s.group] || '') + '</th></tr>'; }
    const incl = s.group === 'country' ? '<input type="checkbox" data-incl="' + esc(s.key) + '"' + (state.excl[s.key] ? '' : ' checked') +
      ' title="Count this country in the All uploads rows"> ' : '';
    h += '<tr><th>' + incl + esc(s.label) + esc(allNote(s, tallies)) + '</th>';
    for (const r of on) {
      if (s.errorsOnly && r.key !== 'wrong') { h += '<td class="inc" title="Lookalike uploads are judged on wrong matches only">n/a</td>'; continue; }
      const bv = bi.map(i => share(tallies[i][s.key], r.outs)), cv = ci.map(i => share(tallies[i][s.key], r.outs));
      const events = pick(bv.concat(cv), 'mean') * tallies[bi[0]][s.key].n / 100;
      const v = verdictFor(s.key, bv, cv);
      const word = events < state.minEvents ? 'inconclusive' : v.status;
      counts[word]++;
      h += '<td class="' + (word === 'inconclusive' ? 'inc' : word) + '" title="baseline ' + v.b.toFixed(2) + '% vs ' +
        esc(state.chal) + ' ' + v.c.toFixed(2) + '%; about ' + Math.round(events) + ' uploads per run">' + word +
        '<br><small>' + v.b.toFixed(1) + ' to ' + v.c.toFixed(1) + ' (' + (v.diff >= 0 ? '+' : '') + v.diff.toFixed(1) + ')</small></td>';
    }
    h += ruleCell(s) + thrCell(s, g0) + '</tr>';
  }
  return '<div class="spread"><b>' + counts.regress + '</b> regress, <b>' + counts.improve + '</b> improve, <b>' + counts.same +
    '</b> same, <b>' + counts.inconclusive + '</b> inconclusive (slice by rule cells).</div>' + h + '</table>';
}

function bandSection(s, tallies) {
  const mix = D.mix[s.key];
  let body = '';
  for (const g of GROUPS) {
    const ts = groupIdx(g).map(i => tallies[i][s.key]).filter(Boolean);
    if (!ts.length) continue;
    let segs = '', rows = '';
    for (const o of OUT) {
      const vals = ts.map(t => 100 * (t.counts[o.key] || 0) / t.n);
      const av = pick(vals, 'mean'), mn = pick(vals, 'min'), mx = pick(vals, 'max');
      if (mx > 0) {
        const label = av >= 17 ? o.short + ' ' + Math.round(av) + '%' : (av >= 6 ? Math.round(av) + '%' : '');
        segs += '<span class="seg ' + o.css + '" style="width:' + av.toFixed(3) + '%" title="' +
          esc(o.label + ': average ' + av.toFixed(1) + '%, lowest ' + mn.toFixed(1) + '%, highest ' + mx.toFixed(1) + '%') + '">' + esc(label) + '</span>';
      }
      rows += '<tr><td><i class="sw ' + o.css + '"></i>' + esc(o.short) + '</td><td>' + av.toFixed(1) + '</td><td>' +
        mn.toFixed(1) + '</td><td>' + mx.toFixed(1) + '</td></tr>';
    }
    const pv = ts.map(t => { const a = t.counts.correctly_matched || 0, b = t.counts.incorrect_match || 0; return a + b ? 100 * a / (a + b) : NaN; })
      .filter(x => !isNaN(x));
    if (pv.length) rows += '<tr><td><i class="sw"></i>Precision of auto-accepted</td><td>' + pick(pv, 'mean').toFixed(1) + '</td><td>' +
      pick(pv, 'min').toFixed(1) + '</td><td>' + pick(pv, 'max').toFixed(1) + '</td></tr>';
    body += '<div class="run"><div class="runlabel"><b>' + esc(g) + '</b><span class="meta">' + ts.length + ' runs, average</span></div><div>' +
      '<div class="bar">' + segs + '</div><table class="band"><tr><th>Outcome</th><th>Average %</th><th>Lowest %</th><th>Highest %</th></tr>' +
      rows + '</table></div></div>';
  }
  const cut = (nExcl() && (s.key === 'ALL' || s.key === 'LOOK')) || (state.weighted && s.key === 'ALL');
  return '<section><h2>' + esc(s.label) + '<small>' + (cut ? esc(allNote(s, tallies)) : mix ? mix.n + ' uploads' : '') + '</small></h2>' +
    '<div class="mix">' + (mix && !cut ? mix.match + ' have an existing facility, ' + mix.new + ' are genuinely new' : '') + '</div>' + body + '</section>';
}

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
  const ok = t.counts.correctly_matched || 0, bad = t.counts.incorrect_match || 0;
  const prec = ok + bad ? '<div class="cap"><b>Precision of auto-accepted</b> ' + (100 * ok / (ok + bad)).toFixed(1) + '% (' +
    ok + ' right of ' + (ok + bad) + ')</div>' : '';
  return '<div class="bar" role="img" aria-label="' + esc(plain.join('; ')) + '">' + segs.join('') + '</div>' +
         '<div class="cap">' + cap.join(' &middot; ') + '</div>' + prec;
}

// The four ways of judging a gap; a slice can use its own instead of the page-wide setting.
const RULESETS = {
  noise: {label: 'Noise-based'},
  benefit: {label: 'Benefit of the doubt', reg: {ref: 'worst', val: 'best'}, imp: {ref: 'best', val: 'worst'}},
  avg: {label: 'Averages', reg: {ref: 'mean', val: 'mean'}, imp: {ref: 'mean', val: 'mean'}},
  nobenefit: {label: 'No benefit of the doubt', reg: {ref: 'best', val: 'worst'}, imp: {ref: 'worst', val: 'best'}},
};
let state = {auto: DEF.auto, floor: DEF.floor, bauto: DEF.auto, bfloor: DEF.floor, view: D.runs.length > 8 ? 'band' : 'run',
  rules: {dup: true, wrong: true, review: true}, reg: {ref: 'worst', val: 'best'}, imp: {ref: 'best', val: 'worst'},
  margin: 0, minEvents: 30, mode: 'range', k: 2, clean: false, chal: CHAL, thr: {}, link: true, ovr: {}, promote: 0, hold: 0, excl: {}, ruleBy: {}, weighted: false, wset: 0};
const exclKey = () => Object.keys(state.excl).sort().join(',');
for (const g of CHALS) state.thr[g] = {auto: DEF.auto, floor: DEF.floor};
if (D.start && CHALS.includes(D.start.group)) {   // open on a chosen model and pair (--start)
  state.chal = D.start.group; state.auto = D.start.auto; state.floor = D.start.floor;
  for (const g of (state.link ? CHALS : [state.chal])) state.thr[g] = {auto: D.start.auto, floor: D.start.floor};
}
const baseCache = {};
function baseTallies(clean) { const k = clean + '|' + exclKey() + '|' + state.weighted + ':' + state.wset; return baseCache[k] || (baseCache[k] = D.runs.map(r => tally(r, DEF.floor, DEF.auto, clean, undefined, undefined, state.excl))); }

const GROUP_TITLE = {all: 'All uploads together', region: 'By region (the groups of countries used for regional models)', country: 'By country', look: 'Lookalike uploads (any candidate is a near-identical sibling), overall and by country'};
// Give one country its own challenger bar or floor (the other one starts at the current default).
function setOvr(cc, which, value) {
  const g = state.thr[state.chal] || {auto: state.auto, floor: state.floor};
  const o = state.ovr[cc] || {auto: g.auto, floor: g.floor};
  o[which] = Math.round(value * 100) / 100;
  if (o.floor > o.auto) { if (which === 'auto') o.floor = o.auto; else o.auto = o.floor; }
  state.ovr[cc] = o;
  render();
}

const baseTallyCache = {};
function render() {
  // The sliders move every challenger together (link on) or only the selected one (link off).
  if (CHALS.length) for (const g of (state.link ? CHALS : [state.chal])) state.thr[g] = {auto: state.auto, floor: state.floor};
  const changed = state.auto !== DEF.auto || state.floor !== DEF.floor || (CHALS.length && (state.bauto !== DEF.auto || state.bfloor !== DEF.floor)) ||
    Object.values(state.thr).some(t => t.auto !== DEF.auto || t.floor !== DEF.floor) || Object.keys(state.ovr).length > 0 || state.promote > 0 || state.hold > 0;
  // With a challenger the baseline keeps its own thresholds (production's by default), so the
  // sliders can be used to ask whether the challenger does better at different settings.
  const thr = r => {
    if (!CHALS.length) return [state.floor, state.auto, null, null];
    if ((r.group || 'baseline') === 'baseline') return [state.bfloor, state.bauto, null, null];
    const t = state.thr[r.group]; return [t.floor, t.auto, state.ovr, {promote: state.promote, hold: state.hold}];
  };
  const tallies = D.runs.map((r, i) => {
    const [f, a, ov, rule] = thr(r);
    if (!CHALS.length || ov) return tally(r, f, a, state.clean, ov, rule, state.excl);
    const key = f + '|' + a + '|' + state.clean + '|' + exclKey() + '|' + state.weighted + ':' + state.wset, c = baseTallyCache[i];   // baseline runs only change with their own sliders
    if (c && c.key === key) return c.t;
    const t = tally(r, f, a, state.clean, undefined, undefined, state.excl); baseTallyCache[i] = {key, t}; return t;
  });
  const bt = baseTallies(state.clean);
  const out = [];
  let lastGroup = null;
  for (const s of D.show) {
    if (s.group !== lastGroup) { lastGroup = s.group; out.push('<h3 class="grp">' + esc(GROUP_TITLE[s.group] || '') + '</h3>'); }
    if (state.view === 'band') { out.push(bandSection(s, tallies)); continue; }
    const mix = D.mix[s.key];
    let rows = '';
    D.runs.forEach((r, i) => {
      rows += '<div class="run"><div class="runlabel"><b>' + esc(r.id) + '</b><span class="meta">' + esc(r.meta) +
        '</span></div><div>' + barHtml(tallies[i][s.key], bt[i][s.key], changed) + '</div></div>';
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
    const cut = (nExcl() && (s.key === 'ALL' || s.key === 'LOOK')) || (state.weighted && s.key === 'ALL');
    out.push('<section><h2>' + esc(s.label) + '<small>' + (cut ? esc(allNote(s, tallies)) : mix ? mix.n + ' uploads' : '') + '</small></h2>' +
      '<div class="mix">' + (mix && !cut ? mix.match + ' have an existing facility, ' + mix.new + ' are genuinely new' : '') +
      '</div>' + rows + spread + '</section>');
  }
  document.getElementById('bars').innerHTML = out.join('');
  const mxEl = document.getElementById('matrix'), keep = mxEl.scrollTop;   // keep the table where the user was
  mxEl.innerHTML = matrixHtml(tallies);
  mxEl.scrollTop = keep;
  document.getElementById('regpanel').hidden = !CHALS.length;
  document.getElementById('chalsel').hidden = CHALS.length < 2;
  document.getElementById('linkwrap').hidden = CHALS.length < 2;
  document.getElementById('autoOut').textContent = state.auto.toFixed(2);
  document.getElementById('floorOut').textContent = state.floor.toFixed(2);
  document.getElementById('bautoOut').textContent = state.bauto.toFixed(2);
  document.getElementById('bfloorOut').textContent = state.bfloor.toFixed(2);
  document.getElementById('baserow').hidden = !CHALS.length;
  document.getElementById('thrWho').textContent = !CHALS.length ? 'Thresholds for all runs' : state.link || CHALS.length < 2
    ? 'Challenger thresholds, for every challenger group (the baseline has its own, below)'
    : 'Thresholds for ' + state.chal + ' only (the baseline and the other challengers keep their own)';
  document.getElementById('changed').textContent = changed ? 'Changes vs default are shown next to each count.' : 'At the default thresholds.';
}

function setState(auto, floor, from) {
  auto = Math.round(auto * 100) / 100; floor = Math.round(floor * 100) / 100;
  if (floor > auto) { if (from === 'auto') floor = auto; else auto = floor; }
  state.auto = auto; state.floor = floor;
  document.getElementById('auto').value = auto; document.getElementById('floor').value = floor;
  render();
}
function setBase(auto, floor, from) {
  auto = Math.round(auto * 100) / 100; floor = Math.round(floor * 100) / 100;
  if (floor > auto) { if (from === 'auto') floor = auto; else auto = floor; }
  state.bauto = auto; state.bfloor = floor;
  document.getElementById('bauto').value = auto; document.getElementById('bfloor').value = floor;
  render();
}
if (typeof document !== 'undefined') {
  const mx = document.getElementById('matrix');
  const own = e => e.target && e.target.dataset && e.target.dataset.cc;
  // While a slider is dragged only its number moves; the table recalculates when it is released.
  mx.addEventListener('input', e => {
    const out = own(e) && e.target.nextElementSibling;
    if (out && out.tagName === 'OUTPUT') out.textContent = (+e.target.value).toFixed(2);
  });
  mx.addEventListener('change', e => { if (own(e) && e.target.dataset.w !== 'reset') setOvr(e.target.dataset.cc, e.target.dataset.w, +e.target.value); });
  mx.addEventListener('click', e => {
    if (own(e) && e.target.dataset.w === 'reset') { delete state.ovr[e.target.dataset.cc]; render(); }
    if (e.target.dataset && e.target.dataset.inclAll !== undefined) {   // tick or untick every country at once
      state.excl = {};
      if (e.target.dataset.inclAll === '0') D.show.forEach(s => { if (s.group === 'country') state.excl[s.key] = true; });
      render();
    }
  });
  mx.addEventListener('change', e => {   // the rule choosers
    const d = e.target && e.target.dataset;
    if (!d) return;
    if (d.rule !== undefined) { if (e.target.value) state.ruleBy[d.rule] = e.target.value; else delete state.ruleBy[d.rule]; render(); }
    if (d.ruleAll !== undefined && e.target.value) { D.show.forEach(s => { if (s.group === 'all' || s.group === 'region' || s.group === 'country') state.ruleBy[s.key] = e.target.value; }); render(); }
  });
  mx.addEventListener('change', e => {
    const cc = e.target && e.target.dataset && e.target.dataset.incl;
    if (cc === undefined) return;
    if (e.target.checked) delete state.excl[cc]; else state.excl[cc] = true;
    render();
  });
  const wt = document.getElementById('weighted');
  if (wt) wt.addEventListener('change', e => { state.weighted = e.target.checked; render(); });
  const wsel = document.getElementById('wset');
  if (wsel) wsel.addEventListener('change', e => { state.wset = +e.target.value; if (state.weighted) render(); });
  document.getElementById('clearovr').addEventListener('click', () => { state.ovr = {}; render(); });
  document.getElementById('promote').addEventListener('input', e => { state.promote = +e.target.value || 0; render(); });
  document.getElementById('hold').addEventListener('input', e => { state.hold = +e.target.value || 0; render(); });
  const chalsel = document.getElementById('chalsel');
  chalsel.innerHTML = CHALS.map(g => '<option value="' + esc(g) + '">' + esc(g) + '</option>').join('');
  chalsel.value = state.chal;
  chalsel.addEventListener('change', e => {
    if (!state.link) state.thr[state.chal] = {auto: state.auto, floor: state.floor};
    state.chal = e.target.value;
    if (state.link) { render(); return; }
    const t = state.thr[state.chal]; setState(t.auto, t.floor, 'auto'); });
  document.getElementById('linkchal').addEventListener('change', e => { state.link = e.target.checked; render(); });
  document.getElementById('bauto').addEventListener('input', e => setBase(+e.target.value, state.bfloor, 'auto'));
  document.getElementById('bfloor').addEventListener('input', e => setBase(state.bauto, +e.target.value, 'floor'));
  document.getElementById('bsync').addEventListener('click', () => setBase(state.auto, state.floor, 'auto'));
  document.getElementById('bprod').addEventListener('click', () => setBase(DEF.auto, DEF.floor, 'auto'));
  document.getElementById('bauto').value = DEF.auto; document.getElementById('bfloor').value = DEF.floor;
  document.getElementById('auto').addEventListener('input', e => setState(+e.target.value, state.floor, 'auto'));
  document.getElementById('floor').addEventListener('input', e => setState(state.auto, +e.target.value, 'floor'));
  document.querySelectorAll('[data-a]').forEach(b => b.addEventListener('click', () => setState(+b.dataset.a, +b.dataset.f, 'auto')));
  document.querySelectorAll('input[name=labels]').forEach(r => r.addEventListener('change', e => { state.clean = e.target.value === 'clean'; render(); }));
  document.querySelectorAll('input[name=view]').forEach(r => r.addEventListener('change', e => { state.view = e.target.value; render(); }));
  RULES.forEach(r => document.getElementById('rule_' + r.key).addEventListener('change', e => { state.rules[r.key] = e.target.checked; render(); }));
  const regIds = {regref: ['reg', 'ref'], regval: ['reg', 'val'], impref: ['imp', 'ref'], impval: ['imp', 'val']};
  const sync = () => { for (const [id, [k, f]] of Object.entries(regIds)) document.getElementById(id).value = state[k][f]; };
  for (const id of Object.keys(regIds)) document.getElementById(id).addEventListener('change', e => {
    state[regIds[id][0]][regIds[id][1]] = e.target.value; state.mode = 'range'; render(); });
  document.getElementById('margin').addEventListener('input', e => { state.margin = +e.target.value || 0; render(); });
  document.getElementById('minev').addEventListener('input', e => { state.minEvents = +e.target.value || 0; render(); });
  document.querySelectorAll('[data-p]').forEach(b => b.addEventListener('click', () => {
    if (b.dataset.p === 'noise') { state.mode = 'noise'; render(); return; }
    const [rr, rv, ir, iv] = b.dataset.p.split(',');
    state.mode = 'range'; state.reg = {ref: rr, val: rv}; state.imp = {ref: ir, val: iv}; sync(); render(); }));
  document.getElementById('kz').addEventListener('input', e => { state.k = +e.target.value || 0; state.mode = 'noise'; render(); });
  document.getElementById('auto').value = state.auto; document.getElementById('floor').value = state.floor;
  sync();
  document.querySelectorAll('input[name=view]').forEach(r => { r.checked = r.value === state.view; });
  render();
}
"""


def load_scores(path):
    """Read a scores CSV (match_id, retrained_conf) into {match_id: float}."""
    with open(path, newline="") as f:
        return {r["match_id"]: float(r["retrained_conf"]) for r in csv.DictReader(f)}


def load_retrieval(path):
    """Read a retrieval CSV (match_id, retrieved, score) into {match_id: bool}."""
    with open(path, newline="") as f:
        return {r["match_id"]: r["retrieved"] == "1" for r in csv.DictReader(f)}


# Names for the groups of countries used by the regional models (regions.tsv in the handoff folder).
REGION_LABELS = {"south_asia": "South Asia", "southeast_asia": "Southeast Asia", "greater_china": "Greater China",
                 "latam_iberia": "Latin America and Iberia", "us": "United States", "uk_ireland": "UK and Ireland",
                 "west_europe": "Western and Central Europe", "east_europe": "Eastern Europe", "turkey": "Turkey",
                 "mena": "Middle East and North Africa", "korea_japan": "Korea and Japan", "canada": "Canada",
                 "aus_nz": "Australia and New Zealand", "ss_africa": "Sub-Saharan Africa"}


def load_regions(path):
    """Read regions.tsv (name<TAB>comma-separated country codes) into {country code: region key}, where the
    key looks like "REG:south_asia". Returns {} when no file is given."""
    out = {}
    if not path:
        return out
    with open(path) as f:
        for line in f:
            if line.strip():
                name, codes = line.rstrip("\n").split("\t")
                for c in codes.split(","):
                    out[c.strip().lower()] = "REG:" + name
    return out


def country_label(code):
    """A country's name and code, e.g. "Netherlands (nl)". The name comes from pycountry
    when it is installed; otherwise the code alone is shown, so the page never needs it."""
    try:
        import pycountry
        found = pycountry.countries.get(alpha_2=code.upper())
        if found:
            return f"{found.name} ({code})"
    except ImportError:
        pass
    return code.upper()


def load_pick_one(path):
    """Read pick_one_flags.csv (match_id, pick_one) into the set of match_ids that are sibling-pick
    rejections: the moderator chose another near-identical candidate, so the rejected pair may be a
    true match."""
    if not path:
        return set()
    with open(path, newline="") as f:
        return {r["match_id"] for r in csv.DictReader(f) if r["pick_one"].strip().lower() == "true"}


def load_ids(path):
    """Read a file of match_ids, one per line, into a set (empty if no path)."""
    if not path:
        return set()
    with open(path) as f:
        return {ln.strip() for ln in f if ln.strip()}


def build_data(pairs_path, score_specs, min_uploads, auto, floor, retrieval_specs=(), run_groups=None,
               flags_path=None, exclude_ids=None, regions_path=None, weight_sets=None, start=None):
    """Group pairs into uploads and assemble everything the page needs.

    retrieval_specs ("NAME=PATH", made with verify_retrain.py --retrieval-all) says,
    per pair, whether the search rules returned that facility for that upload. A
    run named there must cover every pair it has a score for. Runs without one
    treat every candidate as retrieved.

    exclude_ids is a set of match_ids that some compared model was trained on. Any upload containing one of
    them is left out, so no model is scored on a pair it learned from.

    flags_path (pick_one_flags.csv) marks which rejected candidates are sibling picks, so the page can
    offer the "clean" view that drops them. Without it that view changes nothing.

    Returns (data dict for the page, stats dict for the provenance note)."""
    pick_one = load_pick_one(flags_path)
    region_of = load_regions(regions_path)
    runs_scores = []
    for spec in score_specs:
        name, _, path = spec.partition("=")
        runs_scores.append((name, path, load_scores(path)))
    retrievals = {}
    for spec in retrieval_specs:
        name, _, path = spec.partition("=")
        retrievals[name] = load_retrieval(path)
    common = set.intersection(*(set(s) for _, _, s in runs_scores))
    for name, got in retrievals.items():
        short = len(common - set(got))
        if short:
            sys.exit(f"retrieval file for {name} is missing {short} of the {len(common)} scored pairs. "
                     "Re-run verify_retrain.py with --retrieval-all.")

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
            confirmed = r["status"] == "CONFIRMED"
            lookalike = is_lookalike({"name_l": (r["item_clean_name"] or r["item_name"] or "").upper(),
                                      "name_r": (r["fac_name"] or "").upper()})
            groups[(left["country"], left["name"], left["address"])].append(
                (int(mid) if mid.isdigit() else mid, mid, confirmed, left == right,
                 (not confirmed) and mid in pick_one, lookalike))
            used += 1

    uploads, upload_scores = [], [[] for _ in runs_scores]
    upload_ret = [[] for _ in runs_scores]
    ambiguous = 0
    countries = sorted({k[0] for k in groups})
    cidx = {c: i for i, c in enumerate(countries)}
    mix = collections.defaultdict(lambda: {"n": 0, "match": 0, "new": 0})
    excluded = 0
    for key in sorted(groups):
        cands = sorted(groups[key])
        if exclude_ids and any(c[1] in exclude_ids for c in cands):
            excluded += 1
            continue
        confirmed = [i for i, c in enumerate(cands) if c[2]]
        if len(confirmed) > 1:
            ambiguous += 1
            continue
        true_idx = confirmed[0] if confirmed else -1
        look = any(c[5] for c in cands)
        uploads.append([cidx[key[0]], true_idx, "".join("1" if c[3] else "0" for c in cands),
                        "".join("1" if c[4] else "0" for c in cands), 1 if look else 0])
        for ri, (_, _, sc) in enumerate(runs_scores):
            upload_scores[ri].append([round(sc[c[1]], 4) for c in cands])
            if runs_scores[ri][0] in retrievals:
                got = retrievals[runs_scores[ri][0]]
                upload_ret[ri].append("".join("1" if got[c[1]] else "0" for c in cands))
        for k in ("ALL", key[0]) + ((region_of[key[0]],) if key[0] in region_of else ()) + (("LOOK", "LOOK:" + key[0]) if look else ()):
            m = mix[k]
            m["n"] += 1
            m["match" if true_idx >= 0 else "new"] += 1

    def by_size(codes, prefix=""):
        """The slice keys in `codes`, busiest first, so the page lists the countries with the most uploads at the top."""
        return sorted(codes, key=lambda c: -mix[prefix + c]["n"])

    show = [{"key": "ALL", "label": "All uploads", "group": "all"}]
    for rk in dict.fromkeys(region_of.values()):          # one slice per group of countries, in file order
        if rk in mix:
            show.append({"key": rk, "label": REGION_LABELS.get(rk[4:], rk[4:]), "group": "region"})
    pinned = {c for c, _ in PINNED}
    pinned_name = dict(PINNED)
    show += [{"key": c, "label": f"{n} ({c})", "group": "country"} for c, n in PINNED if c in mix]
    others = by_size(c for c in mix if ":" not in c and c not in ("ALL", "LOOK") and c not in pinned
                     and mix[c]["n"] >= min_uploads)
    show += [{"key": c, "label": country_label(c), "group": "country"} for c in others]
    # The lookalike class cuts across the countries, so it gets a section of its own: overall,
    # then the same countries (pinned first), judged on wrong matches only.
    if "LOOK" in mix:
        show.append({"key": "LOOK", "label": "All lookalike uploads", "group": "look", "errorsOnly": True})
        look_codes = [c[5:] for c in mix if c.startswith("LOOK:")]
        look_pinned = [c for c, _ in PINNED if c in look_codes]
        look_rest = by_size((c for c in look_codes if c not in pinned and mix["LOOK:" + c]["n"] >= min_uploads), "LOOK:")
        show += [{"key": "LOOK:" + c, "group": "look", "errorsOnly": True,
                  "label": f"{pinned_name[c]} ({c})" if c in pinned_name else country_label(c)}
                 for c in look_pinned + look_rest]

    data = {
        "outcomes": [{"key": k, "label": lab, "short": SHORT[k], "css": css, "meaning": m}
                     for k, lab, m, css in OUTCOMES],
        "causes": CAUSE_TEXT, "defaults": {"auto": auto, "floor": floor},
        "countries": countries, "show": show, "mix": mix, "uploads": uploads, "hasFlags": bool(pick_one),
        "regionOf": region_of, "weightSets": [{"label": label, "weights": w} for label, w in (weight_sets or [])],
        "start": ({"group": start[0], "auto": start[1], "floor": start[2]} if start else None),
        "runs": [dict({"id": name, "group": (run_groups or {}).get(name, "baseline"), "scores": upload_scores[i],
                       "meta": os.path.basename(path) + ("" if name in retrievals else " (no retrieval check)")},
                      **({"ret": upload_ret[i]} if name in retrievals else {}))
                 for i, (name, path, _) in enumerate(runs_scores)],
    }
    stats = {"pairs_used": used, "pairs_without_score": skipped,
             "uploads_usable": len(uploads), "uploads_ambiguous_left_out": ambiguous,
             "with_match": mix["ALL"]["match"], "new": mix["ALL"]["new"], "uploads_excluded_trained_on": excluded}
    return data, stats


def load_weights(path):
    """Read a production-volume CSV (a country column, then one count column) into {lowercase country code: count}.
    Rows with a blank country or a count that is not a whole number are skipped."""
    out = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = csv.reader(f)
        next(rows, None)
        for row in rows:
            if len(row) >= 2 and row[0].strip() and row[1].strip().isdigit():
                out[row[0].strip().lower()] = int(row[1].strip())
    return out


def parse_weight_specs(specs, default_label):
    """Turn --weights values into a list of (label, path). A value is "LABEL=PATH", for example
    "last 4 months=volume_4m.csv"; a bare path gets default_label."""
    out = []
    for spec in specs:
        label, sep, path = spec.rpartition("=")
        out.append((label, path) if sep and label else (default_label, spec))
    return out


def parse_presets(specs):
    """Turn --preset values of the form "LABEL=AUTO/FLOOR" (for example "6k best=0.76/0.30") into a list of
    (label, auto, floor). The auto bar comes first, as on the page's sliders. Exits with a plain message on a
    value that does not match that form or is outside 0 to 1."""
    out = []
    for spec in specs:
        label, _, pair = spec.rpartition("=")
        auto, _, floor = pair.partition("/")
        try:
            auto_v, floor_v = float(auto), float(floor)
        except ValueError:
            sys.exit(f'--preset "{spec}": expected LABEL=AUTO/FLOOR, for example "6k best=0.76/0.30"')
        if not label or not (0 <= auto_v <= 1 and 0 <= floor_v <= 1):
            sys.exit(f'--preset "{spec}": needs a label, and both numbers between 0 and 1')
        out.append((label, auto_v, floor_v))
    return out


def preset_buttons(presets):
    """The HTML for extra threshold preset buttons, one per (label, auto, floor), each showing "label (auto / floor)".
    Clicking one sets the page's challenger sliders, the same as the built-in presets."""
    return "".join(f'<button data-a="{a}" data-f="{f}">{html.escape(label)} ({a:.2f} / {f:.2f})</button>'
                   for label, a, f in presets)


def weight_controls(data):
    """The HTML for weighting the overall rows by production volume: a checkbox, plus a menu to choose the period when the page
    has more than one set of weights. Nothing when the page was built without --weights."""
    sets = data.get("weightSets") or []
    if not sets:
        return ""
    menu = ""
    if len(sets) > 1:
        menu = (' <select id="wset">' + "".join(f'<option value="{i}">{html.escape(w["label"])}</option>' for i, w in enumerate(sets)) +
                "</select>")
    what = html.escape(sets[0]["label"]) if len(sets) == 1 else "production volume"
    return (f'<div class="opt"><label><input type="checkbox" id="weighted"> Weight the overall rows by {what}</label>{menu}'
            f' <span class="note">each country counts in proportion to its share, not to its number of uploads here; '
            f'the counts then read as list items</span></div>')


def render_page(data, stats, pairs_path, presets=()):
    """Wrap the data in the page: controls, legend, caveats, and the script. `presets` is a list of
    (label, auto, floor) added as extra threshold buttons beside the built-in ones."""
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
        "competing candidates are undercounted and \"several above the bar\" is an underestimate. Where a "
        "run has a retrieval check, a true match the search rules never returned is a Duplicate (never "
        "compared), and a genuinely new upload for which nothing was retrieved counts as correctly new (cause: the search returned nothing). The check indexes only the facilities in this file, so its level depends on that index "
        "size. Runs marked \"no retrieval check\" treat every candidate as retrieved.")
    prov = (f"Built from {html.escape(os.path.basename(pairs_path))} (sha256 "
            f"{sha256_of(pairs_path)[:12]}): {stats['pairs_used']} pairs grouped into "
            f"{stats['uploads_usable'] + stats['uploads_ambiguous_left_out']} uploads by cleaned text and "
            f"country; {stats['uploads_ambiguous_left_out']} uploads with two or more confirmed candidates "
            f"were left out; {stats['uploads_usable']} are shown ({stats['with_match']} with an existing "
            f"facility, {stats['new']} genuinely new)." +
            (f" {stats['uploads_excluded_trained_on']} further uploads were left out because a compared model trained on one of their pairs."
             if stats.get('uploads_excluded_trained_on') else ""))
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Upload outcomes by country</title><style>{BASE_CSS}{EXTRA_CSS}{PAGE_CSS}</style></head>'
        f'<body><main><h1>What happens to uploads, one bar per run</h1>'
        f'<div class="banner">{caveat}</div>'
        f'<div class="panel"><div class="note" id="thrWho"></div><div class="row">'
        f'<div class="ctl"><label for="auto">Auto-match bar (at or above links automatically)'
        f'<output id="autoOut"></output></label><input type="range" id="auto" min="0" max="1" step="0.01"></div>'
        f'<div class="ctl"><label for="floor">Candidate floor (below this a candidate is not offered)'
        f'<output id="floorOut"></output></label><input type="range" id="floor" min="0" max="0.99" step="0.01"></div>'
        f'<div class="presets"><button data-a="{d["auto"]}" data-f="{d["floor"]}">Production now '
        f'({d["auto"]:.2f} / {d["floor"]:.2f})</button><button data-a="0.8" data-f="0.3">Retrain branch (0.80 / 0.30)</button>'
        f'<button data-a="0.75" data-f="0.3">0.75 / 0.30</button>{preset_buttons(presets)}</div></div>'
        f'<div class="row" id="baserow" hidden><div class="ctl"><label for="bauto">Baseline auto-match bar'
        f'<output id="bautoOut"></output></label><input type="range" id="bauto" min="0" max="1" step="0.01"></div>'
        f'<div class="ctl"><label for="bfloor">Baseline candidate floor<output id="bfloorOut"></output></label>'
        f'<input type="range" id="bfloor" min="0" max="0.99" step="0.01"></div>'
        f'<div class="presets"><button id="bprod">Baseline at production ({d["auto"]:.2f} / {d["floor"]:.2f})</button>'
        f'<button id="bsync">Baseline = challenger thresholds</button></div></div>'
        f'<div class="opt">Rejected candidates counted as non-matches: '
        f'<label><input type="radio" name="labels" value="all" checked> all (conservative)</label>'
        f'<label><input type="radio" name="labels" value="clean"> without sibling picks (clean)</label></div>'
        f'<div class="opt">View: <label><input type="radio" name="view" value="band"> Average and range across runs</label>'
        f'<label><input type="radio" name="view" value="run"> One bar per run</label></div>'
        f'{weight_controls(data)}'
        f'<div class="note" id="changed"></div></div>'
        f'<div class="reg" id="regpanel" hidden><b>Regression rules</b> (challenger against baseline; lower is better for all three) '
        f'<label>Compare the baseline with <select id="chalsel"></select></label> '
        f'<span id="linkwrap" hidden><label><input type="checkbox" id="linkchal" checked> Move all challengers together</label></span><br>'
        f'<label><input type="checkbox" id="rule_dup" checked> More duplicates</label>'
        f'<label><input type="checkbox" id="rule_wrong" checked> More incorrect matches</label>'
        f'<label><input type="checkbox" id="rule_review" checked> More human review</label><br>'
        f'<b>Regression test</b>: it regresses if the challenger\'s '
        f'<select id="regval"><option value="best">best run</option><option value="mean">average</option><option value="worst">worst run</option></select> '
        f'is above the baseline\'s '
        f'<select id="regref"><option value="worst">worst run</option><option value="mean">average</option><option value="best">best run</option></select> '
        f'by more than the margin.<br>'
        f'<b>Improvement test</b>: it improves if the challenger\'s '
        f'<select id="impval"><option value="worst">worst run</option><option value="mean">average</option><option value="best">best run</option></select> '
        f'is below the baseline\'s '
        f'<select id="impref"><option value="best">best run</option><option value="mean">average</option><option value="worst">worst run</option></select> '
        f'by more than the margin.<br>'
        f'Margin (points; in noise mode, the smallest gap worth caring about) <input type="number" id="margin" value="0" step="0.5" min="0"> '
        f'Fewest uploads to judge <input type="number" id="minev" value="30" min="0"><br>'
        f'Noise units <input type="number" id="kz" value="2" step="0.5" min="0"> (used by the Noise-based preset)<br>'
        f'<b>Decision rule for the challengers</b> (the baseline keeps production\'s): when several candidates clear the bar, auto-match the top one if it leads by at least '
        f'<input type="number" id="promote" value="0" step="0.01" min="0" max="1"> (0 = production: send to review); '
        f'send to review when the single winner leads the next candidate by less than '
        f'<input type="number" id="hold" value="0" step="0.01" min="0" max="1"> (0 = production: auto-match).<br>'
        f'<button id="clearovr" title="Remove every per-country threshold">Clear all country thresholds</button> '
        f'<span class="note">Each country row, and each region row where there is one, has its own challenger sliders; they apply to every challenger group. A country\'s own setting wins over its region\'s.</span><br>'
        f'<span class="presets"><button data-p="noise" title="A gap counts when it is bigger than the runs\' own wobble">Noise-based</button>'
        f'<button data-p="worst,best,best,worst" title="Only flag what is clearly outside the baseline range">Benefit of the doubt</button>'
        f'<button data-p="mean,mean,mean,mean" title="Compare averages">Averages</button>'
        f'<button data-p="best,worst,worst,best" title="Flag any hint of worse; credit any hint of better">No benefit of the doubt</button></span>'
        f'<div id="matrix"></div></div>'
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
    p.add_argument("--retrieval", action="append", default=[], metavar="NAME=PATH",
                   help="retrieval check for the run of that name (verify_retrain.py --retrieval-all)")
    p.add_argument("--flags", help="pick_one_flags.csv, to enable the clean-labels view")
    p.add_argument("--regions", help="regions.tsv: add a 'by region' section for the groups of countries in it")
    p.add_argument("--exclude-ids", help="file of match_ids (one per line) that a compared model trained on; "
                                         "uploads containing any of them are left out")
    p.add_argument("--group", action="append", default=[], metavar="NAME=GROUP",
                   help="put the run NAME in a group (baseline or challenger); default is baseline")
    p.add_argument("--out", required=True)
    p.add_argument("--min-uploads", type=int, default=1,
                   help="also show other countries with at least this many uploads "
                        "(default 1: every country in the data)")
    p.add_argument("--auto", type=float, default=0.8)
    p.add_argument("--floor", type=float, default=0.5)
    p.add_argument("--weights", action="append", default=[], metavar="[LABEL=]PATH",
                   help='production-volume CSV (country, count), for example "list items since 2026-01-01=volume.csv": adds a '
                        "checkbox that re-weights the overall rows so each country counts in proportion to its production volume; "
                        "repeat it for other periods and the page adds a menu to choose between them")
    p.add_argument("--weights-label", default="production volume",
                   help="the label for a --weights value given as a bare path")
    p.add_argument("--start", metavar="GROUP=AUTO/FLOOR",
                   help='open the page on one model and pair, for example "chal6k=0.76/0.30" (the production presets are unchanged)')
    p.add_argument("--preset", action="append", default=[], metavar="LABEL=AUTO/FLOOR",
                   help="add a threshold button to the page, for example \"6k best=0.76/0.30\" (repeatable)")
    args = p.parse_args()
    presets = parse_presets(args.preset)
    start = parse_presets([args.start])[0] if args.start else None
    data, stats = build_data(args.pairs, args.scores, args.min_uploads, args.auto, args.floor, args.retrieval,
                             dict(g.partition("=")[::2] for g in args.group), args.flags,
                             load_ids(args.exclude_ids), args.regions,
                             [(label, load_weights(path)) for label, path in parse_weight_specs(args.weights, args.weights_label)], start)
    page = render_page(data, stats, args.pairs, presets)
    with open(args.out, "w") as f:
        f.write(page)
    print(f"wrote {args.out} ({len(page) / 1e6:.1f} MB)")
    print(stats)


if __name__ == "__main__":
    main()
