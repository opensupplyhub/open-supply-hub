#!/usr/bin/env python3
"""How stable is the scoring model's regularization pick? OSDEV-3277.

When dedupe trains, the scoring model (a logistic regression) chooses its
regularization strength, "alpha", by cross-validation over six candidate values
(0.00001 to 1). Because the training pairs are fixed, the fitted model is a
function of alpha alone, so the number of distinct scoring models is at most six
however many seeds are tried. This script measures how often each alpha wins.

It also tests a suspected race. With the default settings the library runs the
cross-validation jobs in a THREAD pool that shares a single classifier object;
every job writes its own alpha and weights onto that shared object, so
concurrent jobs can overwrite each other. If that is happening, the pick should
vary between repeats even with the random seed held fixed. A process pool
(num_cores >= 2) gives every job its own copy, so the pick should then be
constant. The script runs both and prints the picks side by side.

Runs inside the api-app image (dedupe 1.9.4, rlr):

  docker run --rm -e PYTHONHASHSEED=0 -e PYTHONWARNINGS=ignore::FutureWarning \
    -v "$PWD/src/dedupe-hub":/dh --entrypoint python api-app:latest \
    /dh/harness/alpha_check.py --training /dh/api/app/data/training.json \
    [--trials 30] [--seed 0]
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_retrain import FIELDS  # noqa: E402


def pick_alphas(X, y, num_cores, trials, seed):
    """Run the library's alpha search `trials` times with the same seed each
    time, and return a Counter of the alpha picked."""
    import numpy
    import rlr
    from rlr.crossvalidation import gridSearch

    picks = collections.Counter()
    for _ in range(trials):
        numpy.random.seed(seed)
        learner = rlr.RegularizedLogisticRegression()
        picks[gridSearch(X, y, learner, num_cores, learner.cv)] += 1
    return picks


def main():
    """Load the training pairs, then compare repeated alpha picks under the
    library's default thread pool and under a process pool."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--training", required=True)
    p.add_argument("--trials", type=int, default=30,
                   help="repeats per setting, all with the same seed (default 30)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--across-seeds", type=int, default=0,
                   help="also run the search once per seed for seeds 0..N-1 and show how "
                        "often each alpha wins (the real spread between restarts)")
    args = p.parse_args()

    import numpy
    from dedupe import Gazetteer, serializer
    from dedupe.api import flatten_training

    with open(args.training) as f:
        pairs = json.load(f, cls=serializer.dedupe_decoder)
    examples, labels = flatten_training(pairs)
    model = Gazetteer(FIELDS)
    X = model.data_model.distances(examples)
    y = numpy.array(labels)
    print(f"{len(y)} training pairs ({int(y.sum())} match), {args.trials} repeats per setting, "
          f"seed fixed at {args.seed}\n", flush=True)

    results = {}
    for label, cores in (("thread pool, shared classifier (the library default)", 0),
                         ("process pool, one classifier per job", 2)):
        picks = pick_alphas(X, y, cores, args.trials, args.seed)
        results[cores] = picks
        print(f"{label}:")
        for alpha, n in sorted(picks.items()):
            print(f"    alpha {alpha:<8g} picked {n} of {args.trials} times")
        print(flush=True)

    if args.across_seeds:
        import rlr
        from rlr.crossvalidation import gridSearch
        across = collections.Counter()
        for s in range(args.across_seeds):
            numpy.random.seed(s)
            learner = rlr.RegularizedLogisticRegression()
            across[gridSearch(X, y, learner, 2, learner.cv)] += 1
        print(f"a different seed each time (seeds 0..{args.across_seeds - 1}), process pool:")
        for alpha, n in sorted(across.items()):
            print(f"    alpha {alpha:<8g} picked {n} of {args.across_seeds} times "
                  f"({n / args.across_seeds:.0%})")
        print(flush=True)

    default_varies = len(results[0]) > 1
    pool_varies = len(results[2]) > 1
    if default_varies and not pool_varies:
        print("VERDICT: with the seed fixed, the default path picks different alphas and the "
              "process pool does not. That is what a race on the shared classifier looks like.")
    elif default_varies and pool_varies:
        print("VERDICT: both settings vary with the seed fixed, so the shared classifier is not "
              "the only source of variation.")
    else:
        print("VERDICT: the pick is constant with the seed fixed in both settings, so there is "
              "no race here; any variation between full runs comes from elsewhere.")


if __name__ == "__main__":
    main()
