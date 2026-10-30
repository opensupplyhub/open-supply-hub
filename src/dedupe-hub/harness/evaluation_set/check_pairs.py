#!/usr/bin/env python3
"""Check a labeled-pairs file before using it with the harness. OSDEV-3277.

Run this on a new pairs file BEFORE freezing a split or training anything. It needs no model and no
database. It answers three questions:

  1. Does the file have the columns the harness reads, and sensible `status` values?
  2. Can it carry upload-level results? The interactive page rebuilds each upload by grouping pairs that
     share the same cleaned upload name, address and country, so it needs every candidate a moderator
     saw for an upload, the confirmed one included. A sample of individual pairs (for example one
     stratified by confidence) splits uploads apart and leaves few usable ones. This script groups the
     pairs the same way the page does (upload_page.build_data) and prints how many uploads come out.
  3. If --flags is given, how many of the file's rejected pairs the pick-one flags cover. A flags file may
     cover more than the pairs file (ours covers the whole database); only a total absence of overlap is flagged.

A pair file that fails check 1 exits with code 1. Check 2 only warns, because what counts as enough
uploads is a judgement; the thresholds are options.

Usage:
  python3 evaluation_set/check_pairs.py --pairs pairs.csv [--flags pick_one_flags.csv] [--min-uploads 1000]

The cleaned-text rule is make_training_json.record, the same one the page and the training builders use,
so the counts here match the page's `uploads_usable` and `uploads_ambiguous_left_out`.
"""
import argparse
import collections
import csv
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
from make_training_json import record  # noqa: E402

REQUIRED = ("match_id", "status", "confidence", "item_clean_name", "item_name", "item_clean_address",
            "item_address", "item_country", "fac_name", "fac_address", "fac_country")
STATUSES = ("CONFIRMED", "REJECTED")
SINGLE_CANDIDATE_WARN = 0.95     # warn when more than this share of uploads has only one candidate. The full pull
                                 # we use is already 77% single-candidate (moderators only see a few candidates per
                                 # upload), so a lower bar would flag a file that works; a random sample of pairs from
                                 # hundreds of thousands is close to 100%


def check(pairs_path, flags_path=None, min_uploads=1000):
    """Read a pairs file and return a report dict: the missing columns, the status counts, how many rows
    repeat a match_id, how the pairs group into uploads, pick-one coverage when flags are given, and a
    list of plain-language warnings. Nothing is printed here."""
    report = {"missing_columns": [], "statuses": collections.Counter(), "rows": 0, "duplicate_match_ids": 0,
              "no_country": 0, "warnings": []}
    with open(pairs_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        report["missing_columns"] = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if report["missing_columns"]:
            return report
        seen, groups, rejected_ids = set(), collections.defaultdict(list), set()
        for r in reader:
            report["rows"] += 1
            report["statuses"][r["status"]] += 1
            if r["match_id"] in seen:
                report["duplicate_match_ids"] += 1
            seen.add(r["match_id"])
            left = record(r["item_clean_name"] or r["item_name"],
                          r["item_clean_address"] or r["item_address"], r["item_country"])
            if not left["country"]:
                report["no_country"] += 1
            groups[(left["country"], left["name"], left["address"])].append(r["status"] == "CONFIRMED")
            if r["status"] == "REJECTED":
                rejected_ids.add(r["match_id"])
    sizes = [len(g) for g in groups.values()]
    ambiguous = sum(1 for g in groups.values() if sum(g) > 1)
    with_match = sum(1 for g in groups.values() if sum(g) == 1)
    report["uploads"] = {"total": len(groups), "usable": len(groups) - ambiguous, "ambiguous_left_out": ambiguous,
                         "with_match": with_match, "new": len(groups) - ambiguous - with_match,
                         "single_candidate_share": (sum(1 for n in sizes if n == 1) / len(sizes)) if sizes else 0.0,
                         "mean_candidates": (sum(sizes) / len(sizes)) if sizes else 0.0}
    if flags_path:
        with open(flags_path, newline="", encoding="utf-8-sig") as f:
            flagged = {r["match_id"] for r in csv.DictReader(f) if str(r["pick_one"]).lower() in ("true", "t", "1")}
        report["flags"] = {"flagged": len(flagged), "in_pairs": len(flagged & seen),
                           "rejected_in_pairs": len(rejected_ids), "flagged_rejected": len(flagged & rejected_ids)}
    report["warnings"] = warnings_for(report, min_uploads)
    return report


def warnings_for(report, min_uploads):
    """The plain-language warnings a report deserves: unusual statuses, repeated ids, too few usable uploads,
    uploads split into single candidates, and pick-one flags that do not line up with the file."""
    out = []
    odd = {s: n for s, n in report["statuses"].items() if s not in STATUSES}
    if odd:
        out.append(f"status values other than CONFIRMED and REJECTED: {dict(odd)}. The harness counts every "
                   "non-CONFIRMED status as a rejection.")
    if report["duplicate_match_ids"]:
        out.append(f"{report['duplicate_match_ids']} rows repeat an earlier match_id; the harness keeps the first.")
    up = report["uploads"]
    if up["usable"] < min_uploads:
        out.append(f"only {up['usable']} usable uploads (fewer than {min_uploads}). Upload-level results will be thin; "
                   "per-country bars will be noisy or empty.")
    if up["single_candidate_share"] > SINGLE_CANDIDATE_WARN:
        out.append(f"{up['single_candidate_share']:.0%} of uploads have a single candidate, which suggests the file is a "
                   "random sample of pairs rather than whole uploads. The page needs every candidate a moderator saw "
                   "(the full pull the harness was built on is about 77%).")
    if "flags" in report:
        fl = report["flags"]
        if fl["flagged"] and not fl["in_pairs"]:
            out.append("none of the flagged ids appear in the pairs file: the flags probably belong to a different file. "
                       "(A flags file that covers more than this pairs file is fine; the harness only looks flags up.)")
        if fl["flagged_rejected"] < fl["in_pairs"]:
            out.append("some flagged ids are not rejected pairs in this file; pick-one flags only make sense on rejections.")
    return out


def render(report):
    """Print a report as short plain text, ending with a one-line verdict."""
    if report["missing_columns"]:
        print("MISSING COLUMNS: " + ", ".join(report["missing_columns"]))
        print("The harness reads: " + ", ".join(REQUIRED) + ". Map or rename your columns, then run again.")
        return
    print(f"rows {report['rows']}   statuses {dict(report['statuses'])}   rows with no country {report['no_country']}")
    up = report["uploads"]
    print(f"uploads (grouped by cleaned name, address and country): {up['total']}")
    print(f"  usable {up['usable']}  (with an existing match {up['with_match']}, genuinely new {up['new']})")
    print(f"  left out for two or more confirmed candidates: {up['ambiguous_left_out']}")
    print(f"  candidates per upload: mean {up['mean_candidates']:.1f}; uploads with a single candidate {up['single_candidate_share']:.0%}")
    if "flags" in report:
        fl = report["flags"]
        print(f"pick-one flags: {fl['flagged']} flagged, {fl['in_pairs']} found in the pairs file, "
              f"{fl['flagged_rejected']} of them rejected pairs (the file has {fl['rejected_in_pairs']} rejected pairs)")
    for w in report["warnings"]:
        print("WARNING: " + w)
    print("VERDICT: " + ("looks usable" if not report["warnings"] else "usable with the warnings above"))


def main(argv=None):
    """Parse the options, check the file, print the report, and exit 1 if columns are missing."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True, help="labeled pairs CSV")
    p.add_argument("--flags", help="pick_one_flags.csv for that pairs file")
    p.add_argument("--min-uploads", type=int, default=1000, help="warn below this many usable uploads (default 1000)")
    args = p.parse_args(argv)
    report = check(args.pairs, args.flags, args.min_uploads)
    render(report)
    if report["missing_columns"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
