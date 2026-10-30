#!/usr/bin/env python3
"""Per-slice report on labeled pairs. OSDEV-3277 AC#2 / AC#3.

evaluate.py reports one set of numbers for the whole held-out half. This reports
the same kind of numbers for each named slice (see slices.py), so a regression
in one country cannot be averaged away by gains elsewhere.

For every model and slice, at one operating point (--auto, --floor), each
evaluation pair lands in exactly one cell, so the shares add up to 100%:

  auto ok     score >= auto bar  and the human said match      (correctly matched)
  auto bad    score >= auto bar  and the human rejected it     (a wrong merge)
  review      floor <= score < auto bar                        (goes to a human)
  missed      score <  floor     and the human said match      (a duplicate)
  none ok     score <  floor     and the human rejected it     (correctly left alone)

The default output is one text bar per slice (the same bars the HTML page draws),
with percentages and counts. --tables adds the numeric table with precision,
recall, AUC and 95% margins.

SAME EVALUATION SET EVERY TIME. Freeze it once with freeze_eval.py, then pass it
with --eval-set. The run then grades on exactly those pairs, refuses to start if
the pairs file or the eval set has changed since it was frozen, and refuses to
start if any model lacks a score for any frozen pair. --exclude-exact drops the
pairs whose cleaned text is identical on both sides, as a view of the same
frozen set.

RUN HISTORY. --history FILE saves this run (one record per model and label view)
and --html FILE draws the whole history: one bar per run under every slice. Use
--run-label to name the run; re-using a label replaces that bar.

LIMITS, read before quoting a number:
  * Pairwise, not per upload. Every pair was the incumbent matcher's own
    candidate, so "missed" here means "scored below the floor", NOT "never
    retrieved". The never-considered segment is drawn only when a retrieval check
    is attached (--retrieval, from verify_retrain.py --retrieval-out). That check
    indexes the evaluation facilities only, not the whole registry, so it is an
    approximation; and it cannot show matches the old system never surfaced, so
    it measures regressions in retrieval, not gains. Picking the right facility
    among millions of competitors needs measure_fanout.py on sampled uploads.
  * Labels are moderator decisions, a proxy for truth. "wrongly matched" counts
    arbitration rejects as errors unless you read the CLEAN view; read both.
  * Margins cover sampling error on this evaluation set only. They do not cover
    run-to-run model variation.

Pure stdlib, like evaluate.py.

Usage:
  python3 display_results/slice_report.py --pairs pairs.csv --eval-set eval_set.csv \
      --scores "base112=scores_base112.csv" --retrieval "base112=retrieval_base112.csv" \
      --run-label base112 \
      --training-file training_112.json --history runs.jsonl --html runs.html \
      [--auto 0.8] [--floor 0.5] [--min-n 300] [--exclude-exact] [--tables] [--csv out.csv]

`prod` (the `confidence` column in the pairs file) is included only in the tables
and CSV; it is a biased baseline (see the HANDOFF notes).
The default operating point is production's, 0.8 / 0.5.
"""
import argparse
import csv
import json
import math
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
from evaluate import (  # noqa: E402
    PROD_AUTO, PROD_GAZ, attach_flags, attach_scores, auc, load_pairs)
from run_history import (  # noqa: E402
    add_runs, legend_text, load_runs, now_utc, render_html, sha256_of, text_bars)
from slices import assign  # noqa: E402

NAN = float("nan")
CELLS = ("n", "n_pos", "auto_ok", "auto_bad", "review", "missed", "none_ok",
         "not_retrieved")


def wilson_half(k, n, z=1.96):
    """Half-width of the Wilson 95% interval for k successes out of n."""
    if n <= 0:
        return NAN
    p = k / n
    denom = 1 + z * z / n
    return z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom


def measure(rows, col, auto, floor):
    """Score one model on one group of pairs and return the numbers as a dict.

    Every pair lands in exactly one cell, decided by the auto bar and the floor:
    auto ok (at or above the bar and a real match), auto bad (at or above the
    bar but not a match, a wrong merge), review (between the floor and the bar),
    missed (below the floor but a real match, a duplicate) and none ok (below
    the floor and not a match). If a retrieval check is attached for this model
    (row[col + "_ret"]), a pair its search rules never retrieved is taken out
    first: a real match becomes not_retrieved (a duplicate), a non-match becomes
    none ok (it could never have been offered). Also returns precision at the
    bar, recall at the bar and recall at the floor, each with a 95% margin.
    Returns None when the model has no scores for any of these pairs.
    """
    sub = [r for r in rows if col in r]
    n = len(sub)
    if not n:
        return None
    pos = sum(r["label"] for r in sub)
    rkey = col + "_ret"
    has_ret = any(rkey in r for r in sub)
    # Without a retrieval check every pair counts as retrieved, as before.
    items = [(r, r.get(rkey, True)) for r in sub]
    not_retrieved = sum(1 for r, g in items if not g and r["label"] == 1)
    auto_ok = sum(1 for r, g in items if g and r[col] >= auto and r["label"] == 1)
    auto_bad = sum(1 for r, g in items if g and r[col] >= auto and r["label"] == 0)
    review = sum(1 for r, g in items if g and floor <= r[col] < auto)
    missed = sum(1 for r, g in items if g and r[col] < floor and r["label"] == 1)
    none_ok = sum(1 for r, g in items if r["label"] == 0 and (not g or r[col] < floor))
    at_floor = sum(1 for r, g in items if g and r[col] >= floor and r["label"] == 1)
    n_auto = auto_ok + auto_bad
    return {
        "n": n,
        "n_pos": pos,
        "n_neg": n - pos,
        "auc": auc([(r["label"], r[col]) for r in sub]),
        "auto_ok": auto_ok,
        "auto_bad": auto_bad,
        "review": review,
        "missed": missed,
        "none_ok": none_ok,
        "not_retrieved": not_retrieved if has_ret else None,
        "precision_auto": auto_ok / n_auto if n_auto else NAN,
        "precision_auto_pm": wilson_half(auto_ok, n_auto),
        "recall_auto": auto_ok / pos if pos else NAN,
        "recall_auto_pm": wilson_half(auto_ok, pos),
        "recall_floor": at_floor / pos if pos else NAN,
        "recall_floor_pm": wilson_half(at_floor, pos),
    }


def pct(x, width=6):
    """Format a 0-1 share as a percentage with one decimal, right-aligned to
    `width`. A missing value (NaN) prints as 'n/a'."""
    return f"{'n/a':>{width}s}" if x != x else f"{x * 100:{width}.1f}"


def print_table(model, mode, slices, col, auto, floor):
    """Print one table: a row per slice, for one model and one label view.

    `slices` is the {name: rows} dict from slices.assign. In the middle block
    the percentages are shares of that slice's pairs and add up to 100. The
    last column is the raw count of wrong auto-merges, which is what the
    lookalike slice is judged on.
    """
    print(f"\n=== {model} | {mode} labels | auto >= {auto}, floor {floor} ===")
    print(f"{'slice':24s} {'n':>6s} {'pos':>5s} {'AUC':>6s} | "
          f"{'autoOK%':>7s} {'autoBAD%':>8s} {'review%':>7s} {'missed%':>7s} {'never%':>7s} "
          f"{'noneOK%':>7s} | {'prec%':>6s} {'+-':>4s} {'rec@auto%':>9s} "
          f"{'+-':>4s} {'rec@floor%':>10s} {'+-':>4s} | {'#bad':>5s}")
    for name, rows in slices.items():
        m = measure(rows, col, auto, floor)
        if m is None or m["n"] == 0:
            print(f"{name:24s} {0:6d}  (no pairs)")
            continue
        n = m["n"]
        print(f"{name:24s} {n:6d} {m['n_pos']:5d} "
              f"{('n/a' if m['auc'] != m['auc'] else format(m['auc'], '.3f')):>6s} | "
              f"{pct(m['auto_ok'] / n, 7)} {pct(m['auto_bad'] / n, 8)} "
              f"{pct(m['review'] / n, 7)} {pct(m['missed'] / n, 7)} "
              f"{pct((m['not_retrieved'] or 0) / n, 7)} "
              f"{pct(m['none_ok'] / n, 7)} | "
              f"{pct(m['precision_auto'])} {pct(m['precision_auto_pm'], 4)} "
              f"{pct(m['recall_auto'], 9)} {pct(m['recall_auto_pm'], 4)} "
              f"{pct(m['recall_floor'], 10)} {pct(m['recall_floor_pm'], 4)} | "
              f"{m['auto_bad']:5d}")


def attach_retrieval(rows, path, col):
    """Attach one model's retrieval check to the rows as row[col + "_ret"].

    `path` is the CSV from verify_retrain.py --retrieval-out (match_id,
    retrieved, score). Returns how many pairs the file covers."""
    got = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            got[r["match_id"]] = r["retrieved"] == "1"
    for r in rows:
        if r["match_id"] in got:
            r[col + "_ret"] = got[r["match_id"]]
    return len(got)


def load_eval_set(path, pairs_path):
    """Read a frozen eval set and check it against its manifest.

    Exits with an explanation if the manifest is missing, or if the pairs file or
    the eval set no longer matches the checksum recorded when it was frozen.
    Returns ({match_id: tags}, manifest).
    """
    mpath = path + ".manifest.json"
    if not os.path.exists(mpath):
        sys.exit(f"{mpath} is missing. Freeze the set with freeze_eval.py first.")
    with open(mpath) as f:
        manifest = json.load(f)
    if sha256_of(pairs_path) != manifest["pairs_sha256"]:
        sys.exit("The pairs file has changed since the evaluation set was frozen "
                 f"({manifest['pairs_file']}). Grading on it would silently change "
                 "the evaluation set. Restore the original file, or freeze a new "
                 "set and start a new history.")
    if sha256_of(path) != manifest["eval_set_sha256"]:
        sys.exit(f"{path} has changed since it was frozen. Restore it, or freeze a new set.")
    tags = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            tags[r["match_id"]] = {"pick_one": r["pick_one"] == "1",
                                   "exact": r["exact_text"] == "1"}
    return tags, manifest


def training_info(path):
    """Best-effort provenance for a training file: name, checksum and pair counts."""
    if not path or not os.path.exists(path):
        return {"file": os.path.basename(path)} if path else None
    info = {"file": os.path.basename(path), "sha256": sha256_of(path)}
    try:
        with open(path) as f:
            t = json.load(f)
        info["match"], info["distinct"] = len(t["match"]), len(t["distinct"])
    except (ValueError, KeyError, OSError):
        pass
    return info


def run_record(run_id, model, mode, slices, col, args, dataset, training, scores_sha):
    """One history record: this model's counts for every slice in one label view."""
    cells = {}
    for name, srows in slices.items():
        m = measure(srows, col, args.auto, args.floor)
        if m is not None:
            cells[name] = {k: m[k] for k in CELLS}
    return {"run_id": run_id, "when": now_utc(), "model": model, "view": mode,
            "unit": "pairs", "operating_point": {"auto": args.auto, "floor": args.floor},
            "training": training, "scores_sha256": scores_sha,
            "dataset": dataset, "slices": cells}


def main():
    """Grade the models on the evaluation set and print, save and draw the results.

    Prints text bars per slice (and optionally tables), can write a long-format
    CSV, can append this run to a history file, and can render the whole history
    as an HTML page with one bar per run under every slice."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True)
    p.add_argument("--eval-set", help="frozen eval_set.csv from freeze_eval.py")
    p.add_argument("--exclude-exact", action="store_true",
                   help="drop pairs whose cleaned text is identical on both sides "
                        "(needs --eval-set)")
    p.add_argument("--flags", help="pick_one_flags.csv; enables the CLEAN view "
                                   "when --eval-set is not used")
    p.add_argument("--scores", action="append", default=[], metavar="NAME=PATH",
                   help="repeatable; scores from verify_retrain.py")
    p.add_argument("--retrieval", action="append", default=[], metavar="NAME=PATH",
                   help="repeatable; the retrieval check for model NAME, from "
                        "verify_retrain.py --retrieval-out. It must cover every "
                        "evaluation pair or it is ignored")
    p.add_argument("--run-label", help="name for this run (one --scores model only); "
                                       "default: the model name")
    p.add_argument("--training-file", help="training file used, recorded in the history")
    p.add_argument("--history", help="append this run to this JSON-lines history file")
    p.add_argument("--html", help="write the outcome-bar page for the history "
                                  "(or for this run if no --history)")
    p.add_argument("--tables", action="store_true", help="also print the numeric tables")
    p.add_argument("--auto", type=float, default=PROD_AUTO,
                   help=f"auto bar (default {PROD_AUTO}, production's)")
    p.add_argument("--floor", type=float, default=PROD_GAZ,
                   help=f"candidate floor (default {PROD_GAZ}, production's)")
    p.add_argument("--min-n", type=int, default=200,
                   help="also list every other country with at least this many "
                        "evaluation pairs (default 200)")
    p.add_argument("--csv", help="write long-format results here (model, labels, "
                                 "slice, metric, value)")
    args = p.parse_args()

    if args.run_label and len(args.scores) != 1:
        sys.exit("--run-label needs exactly one --scores model.")
    if args.exclude_exact and not args.eval_set:
        sys.exit("--exclude-exact needs --eval-set, so the exclusion is a view of "
                 "a frozen set rather than a different dataset.")

    tags = manifest = None
    if args.eval_set:
        # Check the checksums BEFORE parsing anything, so a changed pairs file is
        # refused with an explanation rather than crashing partway through.
        tags, manifest = load_eval_set(args.eval_set, args.pairs)

    rows = load_pairs(args.pairs)
    models = [("prod", "prod")]
    score_paths = {}
    for spec in args.scores:
        name, _, path = spec.partition("=")
        attach_scores(rows, path, name)
        models.append((name, name))
        score_paths[name] = path

    if args.eval_set:
        test = [r for r in rows if r["match_id"] in tags]
        if len(test) != manifest["eval_rows"]:
            sys.exit(f"Only {len(test)} of the {manifest['eval_rows']} frozen pairs "
                     f"are in {args.pairs}.")
        for r in test:
            t = tags[r["match_id"]]
            r["pick_one"], r["exact"] = t["pick_one"], t["exact"]
        for name, col in models[1:]:
            missing = sum(1 for r in test if col not in r)
            if missing:
                sys.exit(f"{name}: no score for {missing} of the {len(test)} frozen "
                         "evaluation pairs. Every model must be scored on every frozen "
                         "pair, or the comparison is not like for like.")
        if args.exclude_exact:
            before = len(test)
            test = [r for r in test if not r["exact"]]
            print(f"excluding pairs with identical text on both sides: "
                  f"{before} -> {len(test)}")
        dataset = {"kind": "frozen", "rows": len(test),
                   "sha256": manifest["eval_set_sha256"], "exclude_exact": args.exclude_exact}
        print(f"evaluation set: FROZEN, {len(test)} pairs, "
              f"sha256 {manifest['eval_set_sha256'][:12]}, "
              f"exact matches excluded: {'yes' if args.exclude_exact else 'no'}")
    else:
        if args.flags:
            attach_flags(rows, args.flags)
        test = [r for r in rows if not r["train"]]
        dataset = {"kind": "hash-split", "rows": len(test), "sha256": None,
                   "exclude_exact": False}
        print(f"evaluation set: held-out half (stable match_id hash), {len(test)} of "
              f"{len(rows)} pairs. NOT frozen: use freeze_eval.py and --eval-set to "
              "guarantee every run is graded on the same pairs.")
    for spec in args.retrieval:
        name, _, path = spec.partition("=")
        if name not in score_paths:
            sys.exit(f"--retrieval {name}: there is no --scores model with that name.")
        attach_retrieval(rows, path, name)
        covered = sum(1 for r in test if name + "_ret" in r)
        if covered < len(test):
            print(f"{name}: the retrieval file covers {covered} of the {len(test)} "
                  "evaluation pairs, so it is ignored (a partial check cannot be turned "
                  "into percentages). Re-run verify_retrain.py without --retrieval-limit.")
            for r in rows:
                r.pop(name + "_ret", None)
        else:
            print(f"{name}: retrieval check attached ({covered} pairs)")
    print("pairwise view: every pair was the incumbent's own candidate; see the "
          "LIMITS note in the docstring.")

    views = [("all", test)]
    if args.eval_set or args.flags:
        clean = [r for r in test if not (r["label"] == 0 and r["pick_one"])]
        views = [("clean", clean)] + views
    else:
        print("no pick-one flags: reporting ALL labels only (raw REJECTED = "
              "negative, the conservative bound)")

    bar_models = models[1:] or models
    training = training_info(args.training_file)
    records, out_rows = [], []
    for mode, data in views:
        slices = assign(data, min_n=args.min_n)
        for model, col in models:
            if args.tables:
                print_table(model, mode, slices, col, args.auto, args.floor)
            for sname, srows in slices.items():
                m = measure(srows, col, args.auto, args.floor)
                if m is None:
                    continue
                for metric, value in m.items():
                    out_rows.append((model, mode, sname, metric, value))
        for model, col in bar_models:
            run_id = args.run_label or model
            rec = run_record(run_id, model, mode, slices, col, args, dataset, training,
                             sha256_of(score_paths[model]) if model in score_paths else None)
            records.append(rec)
            print(f"\n=== {run_id} | {mode} labels | auto >= {args.auto}, floor {args.floor} ===")
            print(legend_text())
            print()
            print("\n".join(text_bars(rec)))

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["model", "labels", "slice", "metric", "value"])
            w.writerows(out_rows)
        print(f"wrote {len(out_rows)} rows to {args.csv}")

    history = records
    if args.history:
        history = add_runs(args.history, [r for r in records if r["model"] != "prod"])
        print(f"history: {len(history)} record(s) in {args.history}")
    if args.html:
        with open(args.html, "w") as f:
            f.write(render_html(history))
        print(f"wrote {args.html}")


if __name__ == "__main__":
    main()
