#!/usr/bin/env python3
"""Build a training file that copies the recipe of the original 112-pair file, at a larger size. OSDEV-3277.

make_training_json.py draws pairs that are mostly hard (lookalike names, or disputed by the old model). The 112 file
is different: it is mostly clean, with a spread of easy and hard pairs. This script measures that file and builds a
new one the same way from the labeled pairs, so we can ask whether the 112's curation, not its size, is what makes
it hard to beat.

What is copied from the 112 file, measured from it rather than assumed:
  * the share of matches to non-matches (47 : 65);
  * how similar the two names of a pair are, as a histogram per class (a match is usually near-identical, a non-match
    is spread from clearly different to lookalike);
  * the share of non-matches that pair facilities from different countries (about 15%);
  * no country takes more than --country-cap of a class.

Real moderator-labeled pairs fill every slot they can. Two kinds of slot cannot be filled from real pairs, because
moderators almost never see them, so they are made: a cross-country non-match, and an easy same-country non-match
(two unrelated facilities from the same country). Both are built from records in the training half of the pairs file,
a record from one pair against a record from another, which is a non-match with near certainty. The match_ids of
every pair or record used go to --ids-out, so a comparison can leave out uploads that contain them.

Only pairs from the training half (hash of match_id) are used. With --eval-set the script refuses to write if any
real pair is in the frozen evaluation set.

Usage:
  python3 training_sets/make_style112.py --pairs pairs.csv --reference training_112.json --eval-set eval_set.csv \
      --total 600 --out training_style112_600.json --ids-out ids_style112_600.txt
"""
import argparse
import difflib
import json
import os
import random
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
from make_training_json import eval_overlap, load_pairs  # noqa: E402

SEED = 42
BIN_EDGES = (0.0, 0.4, 0.6, 0.8, 1.0001)   # name-similarity bins; the last edge is just past 1 so 1.0 is included
TRIES = 400                                 # attempts to make one synthetic pair land in a bin before giving up


def name_sim(left, right):
    """How alike the two cleaned names of a pair are, 0 (nothing shared) to 1 (identical)."""
    return difflib.SequenceMatcher(None, left["name"], right["name"]).ratio()


def bin_of(sim):
    """The index of the name-similarity bin a similarity falls into."""
    for i in range(len(BIN_EDGES) - 1):
        if BIN_EDGES[i] <= sim < BIN_EDGES[i + 1]:
            return i
    return len(BIN_EDGES) - 2


def profile(training):
    """Measure a training.json: the match share, the cross-country share of non-matches, and the share of each
    class that falls in each name-similarity bin. Returns a dict."""
    out = {}
    nbins = len(BIN_EDGES) - 1
    for cls in ("match", "distinct"):
        pairs = [e["__value__"] for e in training[cls]]
        counts = [0] * nbins
        for left, right in pairs:
            counts[bin_of(name_sim(left, right))] += 1
        out[cls] = {"n": len(pairs), "bins": [c / len(pairs) for c in counts],
                    "cross": sum(1 for l, r in pairs if l["country"] != r["country"]) / len(pairs)}
    out["match_share"] = out["match"]["n"] / (out["match"]["n"] + out["distinct"]["n"])
    return out


def quotas(share, n):
    """Turn bin shares into whole-number slots summing to exactly n (largest remainders get the leftovers)."""
    raw = [s * n for s in share]
    got = [int(x) for x in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - got[i], reverse=True)[: n - sum(got)]:
        got[i] += 1
    return got


def draw_real(pool, quota, cap, rng, boost=(), caps=None):
    """Pick real pairs for each bin. `pool` is rows with 'bin' and 'country'; `quota` is slots per bin; `cap` is the
    most rows one country may supply to the whole draw, and `caps` {country: cap} overrides it for chosen countries.
    Within a bin the countries in `boost` are tried first. Slots a bin cannot fill are returned as a shortfall list."""
    by_bin = {}
    for r in pool:
        by_bin.setdefault(r["bin"], []).append(r)
    for rows in by_bin.values():
        rng.shuffle(rows)
        rows.sort(key=lambda r: r["country"] not in boost)     # stable: boosted countries first, order within each is random
    caps = caps or {}
    taken, per_country, short = [], {}, []
    for b, want in enumerate(quota):
        got = 0
        for r in by_bin.get(b, []):
            if got == want:
                break
            if per_country.get(r["country"], 0) >= caps.get(r["country"], cap):
                continue
            per_country[r["country"]] = per_country.get(r["country"], 0) + 1
            taken.append(r)
            got += 1
        short.append(want - got)
    return taken, short


def synthetic(train, want_bin, cross, rng):
    """One made-up non-match: a record from one pair against a record from another. With cross=True the two are
    from different countries; otherwise from the same country. When want_bin is not None the names must land in
    that similarity bin. Returns (left, right, source ids) or None if no such pair turned up."""
    for _ in range(TRIES):
        a, b = rng.choice(train), rng.choice(train)
        if a["match_id"] == b["match_id"]:
            continue
        left, right = a["left"], b["right"]
        if not left["country"] or not right["country"]:
            continue
        if (left["country"] != right["country"]) != cross:
            continue
        if want_bin is not None and bin_of(name_sim(left, right)) != want_bin:
            continue
        return left, right, (a["match_id"], b["match_id"])
    return None


def build(rows, ref, total, country_cap, rng, boost=(), boost_cap=None, limit=(), limit_cap=0.02):
    """Build the style-of-112 training set from labeled `rows`. Returns (training dict, ids used, report dict).

    `boost` countries are drawn first and may supply up to `boost_cap` of a class each (default: twice country_cap
    is not used; the default is country_cap). `limit` countries may supply only `limit_cap` of a class and are never
    used as the source of a made-up pair."""
    train = [r for r in rows if r["train"]]
    for r in train:
        r["bin"] = bin_of(name_sim(r["left"], r["right"]))
    n_match = round(total * ref["match_share"])
    n_distinct = total - n_match
    cap_m, cap_d = max(1, int(n_match * country_cap)), max(1, int(n_distinct * country_cap))
    boost_cap = country_cap if boost_cap is None else boost_cap
    caps_m = {c: max(1, int(n_match * boost_cap)) for c in boost} | {c: max(1, int(n_match * limit_cap)) for c in limit}
    caps_d = {c: max(1, int(n_distinct * boost_cap)) for c in boost} | {c: max(1, int(n_distinct * limit_cap)) for c in limit}
    source = [r for r in train if r["left"]["country"] not in limit and r["right"]["country"] not in limit]

    matches, _ = draw_real([r for r in train if r["label"] == 1], quotas(ref["match"]["bins"], n_match), cap_m, rng, boost, caps_m)
    ids = {r["match_id"] for r in matches}
    examples = {"match": [(r["left"], r["right"]) for r in matches], "distinct": []}
    made = {"cross": 0, "easy": 0}

    quota = quotas(ref["distinct"]["bins"], n_distinct)
    for _ in range(round(n_distinct * ref["distinct"]["cross"])):
        s = synthetic(source, None, True, rng)
        if s:
            examples["distinct"].append((s[0], s[1]))
            ids.update(s[2])
            quota[bin_of(name_sim(s[0], s[1]))] = max(0, quota[bin_of(name_sim(s[0], s[1]))] - 1)
            made["cross"] += 1

    while sum(quota) > n_distinct - len(examples["distinct"]):     # cross-country pairs can outnumber their bin's slots
        quota[quota.index(max(quota))] -= 1

    # Real rejections fill each bin first. Only same-country ones are used, so the cross-country share stays at the target.
    real_pool = [r for r in train if r["label"] == 0 and r["left"]["country"] == r["right"]["country"]]
    taken, short = draw_real(real_pool, quota, cap_d, rng, boost, caps_d)
    for r in taken:
        examples["distinct"].append((r["left"], r["right"]))
        ids.add(r["match_id"])
    for b, missing in enumerate(short):
        for _ in range(missing):
            s = synthetic(source, b, False, rng)
            if s:
                examples["distinct"].append((s[0], s[1]))
                ids.update(s[2])
                made["easy"] += 1

    training = {cls: [{"__class__": "tuple", "__value__": [l, r]} for l, r in pairs] for cls, pairs in examples.items()}
    return training, ids, {"made": made, "real_match": len(matches), "real_distinct": len(taken)}


def main():
    """Measure the reference file, build the new one, print how it compares and write it."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True)
    p.add_argument("--reference", required=True, help="the 112-pair training.json to copy the recipe from")
    p.add_argument("--total", type=int, default=600)
    p.add_argument("--country-cap", type=float, default=0.15, help="most any one country may supply, as a share of a class")
    p.add_argument("--boost", default="", help="comma-separated countries to draw more of (first in each bin)")
    p.add_argument("--boost-cap", type=float, help="most a boosted country may supply, as a share of a class (default: --country-cap)")
    p.add_argument("--limit", default="", help="comma-separated countries to draw little of")
    p.add_argument("--limit-cap", type=float, default=0.02, help="most a limited country may supply, as a share of a class")
    p.add_argument("--eval-set", help="frozen eval_set.csv: refuse to write if a real pair is in it")
    p.add_argument("--out", required=True)
    p.add_argument("--ids-out")
    args = p.parse_args()

    with open(args.reference) as f:
        ref = profile(json.load(f))
    rows = load_pairs(args.pairs)
    training, ids, report = build(rows, ref, args.total, args.country_cap, random.Random(SEED),
                                        boost=[c for c in args.boost.split(",") if c], boost_cap=args.boost_cap,
                                        limit=[c for c in args.limit.split(",") if c], limit_cap=args.limit_cap)
    got = profile(training)

    print(f"reference 112: match share {ref['match_share']:.2f}, non-match cross-country {ref['distinct']['cross']:.2f}")
    print(f"built        : {got['match']['n']} match / {got['distinct']['n']} distinct, match share {got['match_share']:.2f}, "
          f"non-match cross-country {got['distinct']['cross']:.2f}")
    for cls in ("match", "distinct"):
        print(f"  {cls:8} name-similarity bins  112: {[round(x, 2) for x in ref[cls]['bins']]}  new: {[round(x, 2) for x in got[cls]['bins']]}")
    print(f"real pairs: {report['real_match']} match, {report['real_distinct']} non-match; made: {report['made']['cross']} "
          f"cross-country and {report['made']['easy']} easy same-country non-matches")
    for cls in ("match", "distinct"):
        mix = {}
        for e in training[cls]:
            c = e["__value__"][0]["country"]
            mix[c] = mix.get(c, 0) + 1
        print(f"  {cls:8} countries: " + " ".join(f"{c}={n}" for c, n in sorted(mix.items(), key=lambda kv: -kv[1])[:14]))
    if args.eval_set:
        chosen = [r for r in rows if r["match_id"] in ids]
        overlap = eval_overlap(chosen, args.eval_set)
        print(f"overlap with eval set: {overlap} of {len(chosen)} pairs/records used")
        if overlap:
            sys.exit("refusing to write: training pairs are also in the evaluation set")
    with open(args.out, "w") as f:
        json.dump(training, f)
    print(f"wrote {args.out}")
    if args.ids_out:
        with open(args.ids_out, "w") as f:
            f.write("\n".join(sorted(ids)) + "\n")
        print(f"wrote {len(ids)} match_ids to {args.ids_out}")


if __name__ == "__main__":
    main()
