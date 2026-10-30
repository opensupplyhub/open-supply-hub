#!/usr/bin/env python3
"""Compare two models' decisions on the same sampled uploads. OSDEV-3277 traffic test.

Takes two files written by traffic_test.py (model A, usually the 112-pair file at 0.5/0.8, and model B, usually
the 6k file at 0.3/0.75), prints how many uploads each model auto-matches, sends to review, or makes new, overall
and by country, and how often the two agree. Every upload where they differ goes to a CSV a moderator can fill
in: both decisions side by side with the upload's own text and the text of each facility chosen or suggested,
plus an empty `right_answer` column.

The decisions alone say nothing about who is right. Where both models auto-match the same facility, or both
send the upload to review, nothing needs judging. Where they differ, someone has to say which was correct.

  python3 traffic_compare.py --a traffic_112_seed0.csv --b traffic_6k_seed0.csv \
      --sample traffic_sample.csv --index traffic_index.csv --out traffic_disagreements.csv
"""
import argparse
import csv
from collections import Counter

DECISIONS = ("auto_match", "review", "new_facility")


def read_decisions(path):
    """Read a traffic_test.py output into {item_id: row}."""
    with open(path, newline="") as f:
        return {r["item_id"]: r for r in csv.DictReader(f)}


def read_facility_text(path):
    """{facility id: 'name | address'} from traffic_index.csv's facility rows."""
    out = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["kind"] == "facility":
                out[r["facility_id"]] = f"{r['name']} | {r['address']}"
    return out


def disagreement_kind(a, b):
    """Name how two decisions on one upload differ, or None if they agree.

    Two auto-matches agree only if they chose the same facility. Two reviews agree, and two new facilities agree."""
    if a["decision"] == b["decision"]:
        if a["decision"] == "auto_match" and a["chosen"] != b["chosen"]:
            return "both auto-match, different facility"
        return None
    return " vs ".join(sorted((a["decision"], b["decision"])))


def compare(a, b):
    """Compare two decision dictionaries over the uploads both have.

    Returns (by_pair, by_country, disagreements): a Counter of (decision A, decision B), a dict of country ->
    {'n', 'a': Counter, 'b': Counter, 'differ'}, and the list of (item_id, kind) where the models differ."""
    by_pair, by_country, disagreements = Counter(), {}, []
    for item_id in sorted(set(a) & set(b)):
        ra, rb = a[item_id], b[item_id]
        by_pair[(ra["decision"], rb["decision"])] += 1
        c = by_country.setdefault(ra["country"], {"n": 0, "a": Counter(), "b": Counter(), "differ": 0})
        c["n"] += 1
        c["a"][ra["decision"]] += 1
        c["b"][rb["decision"]] += 1
        kind = disagreement_kind(ra, rb)
        if kind:
            c["differ"] += 1
            disagreements.append((item_id, kind))
    return by_pair, by_country, disagreements


def top_text(row, facilities, k=3):
    """The facility the model chose, or else its top candidates, as readable text."""
    if row["chosen"]:
        return f"CHOSE {row['chosen']}: {facilities.get(row['chosen'], '?')}"
    return " // ".join(f"{fac} ({sc}): {facilities.get(fac, '?')}"
                       for fac, sc in [c.split(":") for c in row["candidates"].split(";") if c][:k])


def pct(n, d):
    """n as a percentage of d, one decimal, or '-' if d is zero."""
    return "-" if not d else f"{100 * n / d:.1f}%"


def main():
    """Print the comparison and write the disagreements for a moderator."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--a", required=True, help="decisions from model A (traffic_test.py output)")
    p.add_argument("--b", required=True, help="decisions from model B")
    p.add_argument("--sample", required=True)
    p.add_argument("--index", required=True)
    p.add_argument("--out", required=True, help="disagreements CSV for a moderator")
    p.add_argument("--label-a", default="A")
    p.add_argument("--label-b", default="B")
    args = p.parse_args()

    a, b = read_decisions(args.a), read_decisions(args.b)
    by_pair, by_country, disagreements = compare(a, b)
    n = sum(by_pair.values())
    print(f"{n} uploads scored by both models\n")
    print(f"{'':14}{args.label_a:>14}{args.label_b:>14}")
    for d in DECISIONS:
        na = sum(v for (x, _), v in by_pair.items() if x == d)
        nb = sum(v for (_, y), v in by_pair.items() if y == d)
        print(f"{d:14}{pct(na, n):>14}{pct(nb, n):>14}")
    print(f"\nagree on {pct(n - len(disagreements), n)}; differ on {len(disagreements)} uploads")
    print("\ndisagreements by kind:")
    for kind, v in Counter(k for _, k in disagreements).most_common():
        print(f"  {v:5}  {kind}")
    print(f"\n{'country':8}{'uploads':>8}{'differ':>8}   {args.label_a} auto/review/new     {args.label_b} auto/review/new")
    for country, c in sorted(by_country.items(), key=lambda kv: -kv[1]["n"]):
        fmt = lambda k: "/".join(pct(c[k][d], c["n"]).rstrip("%") for d in DECISIONS)  # noqa: E731
        print(f"{country:8}{c['n']:>8}{c['differ']:>8}   {fmt('a'):<24}{fmt('b')}")

    with open(args.sample, newline="", encoding="utf-8-sig") as f:
        sample = {r["item_id"]: r for r in csv.DictReader(f)}
    facilities = read_facility_text(args.index)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "country", "kind", "upload", "recorded_item_status", "recorded_facility", "created_facility",
                    f"{args.label_a}_decision", f"{args.label_a}_detail", f"{args.label_b}_decision", f"{args.label_b}_detail",
                    "right_answer"])
        for item_id, kind in disagreements:
            s, ra, rb = sample[item_id], a[item_id], b[item_id]
            w.writerow([item_id, s["country"], kind, f"{s['name']} | {s['address']}", s["item_status"], s["recorded_facility"],
                        s["created_facility"], ra["decision"], top_text(ra, facilities), rb["decision"],
                        top_text(rb, facilities), ""])
    print(f"\nwrote {args.out} ({len(disagreements)} rows; fill in right_answer)")


if __name__ == "__main__":
    main()
