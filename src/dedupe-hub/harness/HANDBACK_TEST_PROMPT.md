# Handback test prompt

A prompt for a fresh Claude session (or a person) to check that the OSDEV-3277 harness
and its handback bundle work and nothing is stale. Paste everything below the line into
the session. Replace the four placeholders first:

| placeholder | meaning |
|---|---|
| `<repo>` | your checkout of this repository |
| `<worktree>` | a checkout of branch `osdev-3277-slice-eval` (its harness is `<worktree>/src/dedupe-hub/harness`) |
| `<handback>` | the handback bundle folder, if you have it (tests 3, 7, 8, 9 and 13 need it) |
| `<data>` | the folder holding `pairs.csv`, the frozen evaluation set, the training files and the score files. Facility data: keep it out of git and out of reports |

---

You are testing a finished piece of work for OSDEV-3277 (Open Supply Hub dedupe retrain harness). Your job is to find anything broken, stale or misleading. Do NOT fix things, commit, or push; report findings and ask before changing anything.

## Ground rules
- The work is on branch `osdev-3277-slice-eval`, checked out at `<worktree>`. Harness code: `src/dedupe-hub/harness/`. The branch sits on top of `origin/worktree-osdev-3277-handoff`, and a draft PR into that branch is open.
- `<data>` is facility data. Read only: never modify it and never print rows. Write scratch output only to `$TMPDIR`. Do not write into `<data>` or `<handback>`.
- Use only the Python standard library natively. Docker may be blocked in your sandbox; if so, list the exact docker commands you could not run.
- Never print or quote facility names, addresses or other pair contents in your report.

## What the harness is
Evaluates retrained dedupe matchers on whole uploads using three measures: incorrect matches, duplicates (compared vs never compared), and human review. The files added for this ticket are in folders by what they do: `evaluation_set/`, `training_sets/`, `upload_outcomes/`, `display_results/`, `traffic_replay/`. The original retrain scripts (`make_training_json.py`, `verify_retrain.py`, `evaluate.py`, the experiments, `extract_labels.sql`) stay flat at the top. Each moved file finds its siblings through a path line at its top, so scripts should run from any directory.

## Before you start: check what you have, and ask for what is missing
Do this first. Work out which of the inputs below you actually have, then send the user ONE message that lists, for each missing item, what you need, which tests it blocks, and how they can give it to you (a path, or a command for them to run). Then run every test you can without waiting for an answer, and come back to the blocked ones when the user replies. Never substitute a guess, invent data, or fetch facility data from anywhere other than the paths the user gives you. For facility data ask for a path, never for pasted contents.

| input | needed by | how to check it |
|---|---|---|
| `<worktree>`: a checkout of the branch, and read access to `origin` | 1, 2, 3, 6, 10 | `git -C <worktree> status` and `git ls-remote origin` |
| `<handback>`: the handback bundle folder (and its zip) | 3, 7, 8, 9, 13 | the folder exists and has `README.md`, `HANDBACK.md`, `code/`, `scripts/`, `data/`, `pages/` |
| `<data>`: `pairs.csv`, `eval_set.csv` and `eval_set.csv.manifest.json`, `pick_one_flags.csv`, `training_112.json`, `training_style112_600.json`, `ids_style112_600.txt`, `training_style112_600_plus112.json`, `scores_all_seed*.csv` and `retrieval_all_seed*.csv` (at least seeds 1 and 42), `scores_chal600sp112_seed0.csv` and its retrieval file | 5, 6, 7, 13 | list the folder; do not open the files |
| the original `outcome_bars_UPLOADS_style112.html` and the script that built it | 5 (page bullet) | ask the user where they are |
| `node` | 13 | `node --version` |
| Docker permission and the `api-app:latest` image | the optional Docker run, and the Docker command in test 4 for `traffic_replay/traffic_test.py` | `docker version` |
| a writable `$TMPDIR` | all | `touch "$TMPDIR/x"` |

If something is missing, say so plainly, for example: "I don't have `<data>`, so tests 5, 6, 7 and 13 can't run. Please give me the path to the folder that holds `pairs.csv` and the score files." If a Docker command is blocked, give the user the exact command to run and say what output to paste back.

## Tests to run (report pass, fail or could not run, with evidence)

1. **Unit tests.** From the harness folder run `python3 -B -m unittest discover -p 'test_*.py'`. Expect 84 passing. Also run it from a different directory with `-s` pointing at the harness.
2. **Fresh checkout.** Clone or `git worktree add` the pushed branch `origin/osdev-3277-slice-eval` into `$TMPDIR` (do not touch the existing worktree) and rerun test 1 there. Confirm `git status` is clean and no untracked files are needed.
3. **Patch application** (needs `<handback>`). In a scratch worktree of `origin/worktree-osdev-3277-handoff`, apply `<handback>/code/commits/*.patch` with `git am`. Confirm the result has the same tree as the pushed branch (`git diff` empty). Extract `<handback>/code/harness-snapshot.tgz` and diff it against the branch's harness folder.
4. **Every moved script starts.** Run `--help` for each `.py` under `evaluation_set/`, `training_sets/`, `display_results/` and `traffic_replay/` from `/tmp` (not the harness folder). Any traceback is a failure.
5. **Outputs byte-identical to what already exists** (use `cmp`):
   - `evaluation_set/freeze_eval.py --pairs <data>/pairs.csv --flags <data>/pick_one_flags.csv --out $TMPDIR/x/eval_set.csv` against `<data>/eval_set.csv`.
   - `training_sets/make_style112.py --pairs <data>/pairs.csv --reference <data>/training_112.json --eval-set <data>/eval_set.csv --total 600 --out $TMPDIR/x/t600.json --ids-out $TMPDIR/x/ids.txt` against `<data>/training_style112_600.json` and `<data>/ids_style112_600.txt`. Then `training_sets/merge_training.py --base <data>/training_112.json --add $TMPDIR/x/t600.json --out ...` against `<data>/training_style112_600_plus112.json`.
   - Rebuild a comparison page with `display_results/upload_page.py` into `$TMPDIR` using the same arguments as the page build script that made the existing page (`outcome_bars_UPLOADS_style112.html` in the original handoff folder, if you have it) and compare. Do not overwrite the existing page.
6. **Old layout against new.** `git archive 3cfdd530 src/dedupe-hub/harness` into `$TMPDIR` (the code before the reorganization). Run `slice_report.py` and `pair_page.py` from both old and new on the same inputs (frozen evaluation set, `scores_all_seed42.csv`, `retrieval_all_seed42.csv`); outputs should be identical.
7. **Bundle scripts** (needs `<handback>`). In `<handback>/scripts/`, run `bash make_page.sh` with no arguments (should print usage), a bad spec (should name the problem), and a real small build: `DATA=<data> HARNESS=<worktree>/src/dedupe-hub/harness EXCLUDE=<data>/ids_style112_600.txt bash make_page.sh $TMPDIR/p.html base:all:42,1 mine:chal600sp112:0`. Check that every `.sh` in `<handback>/scripts/` references files that exist (no old flat paths such as `$HARNESS/upload_page.py`, `$HARNESS/make_style112.py` or `/dh/harness/traffic_test.py`). Run `bash -n` on each script.
8. **Docs against reality** (needs `<handback>`): `README.md`, `HANDBACK.md`, `HOWTO-PAGES.md`, `FINDINGS.md`, `PR-DRAFT.md` and the cover note. Check that every file or folder they name exists, that counts (patches, tests, files) are right, and that the `HOWTO-PAGES.md` steps work as written (follow them literally with a scratch data folder: copy the small files from `<handback>/data/`, untar `baseline_runs_20.tgz`, symlink `pairs.csv`). Flag any wording that says the code is "local only" or "not pushed", or that gives an out-of-date commit count.
9. **Zip contents** (needs `<handback>`). `unzip -l` the zip. Confirm it contains no training JSON other than `data/training_112.json`, no `pairs.csv` or other labeled-pair file, and no `.env` or credential-like files. Confirm `eval_set.csv` holds only `match_id`, `country` and two tag columns, and that the zip's file list matches the folder.
10. **Hygiene scan** of the branch diff (`git diff origin/worktree-osdev-3277-handoff..origin/osdev-3277-slice-eval`) and of the handback text files. The repository is public. Look for secrets, tokens, internal Google, Confluence or Slack links or ids, personal paths (`/Users/...`), staff emails or names, and internal board or channel names. Report anything found. A pre-existing comment in `make_training_json.py` about an email found in an address field is known and accepted.
11. **Docstring coverage.** Every module, class and function in the `.py` files under `evaluation_set/`, `training_sets/`, `upload_outcomes/`, `display_results/` and `traffic_replay/`, plus `test_make_training_json.py` and `test_verify_retrain.py`, must have a docstring. Use `ast`.
12. **Dead or unused code.** Report any `.py` in the harness that nothing imports or runs. Do not delete.
13. **Fresh-eyes review** (needs `<handback>` for the numbers). Read `display_results/upload_page.py`'s outcome logic and `upload_outcomes/outcomes.py` against the seven outcomes described in `FINDINGS.md`. Do the docs describe what the code does? Spot-check three numbers in `FINDINGS.md` section 4 using `<handback>/analysis/look.js`, `never.js` and `global_thr.js` against `<handback>/pages/outcome_bars_UPLOADS_1200.html` (run with `node`; read the scripts for their arguments).

14. **Pairs-file checker.** Run `evaluation_set/check_pairs.py --pairs <data>/pairs.csv --flags <data>/pick_one_flags.csv` from `/tmp`. Expect 78,357 rows, 54,279 uploads grouped, 50,045 usable (37,637 with an existing match, 12,408 new), 4,234 left out for two or more confirmed candidates, 77% single-candidate uploads, and the verdict "looks usable" with no warnings. Then try to break it: a copy of `pairs.csv` with a column deleted (exit code 1 and the column named), and a copy with only a small random sample of rows (should warn about thin or fragmented uploads). Check that its counts agree with what a page build prints for `uploads_usable` and `uploads_ambiguous_left_out` (the page also drops uploads containing excluded training pairs and unscored pairs, so expect small differences that those explain).
15. **A different pairs file.** Read the "Using a different pairs file" section of `<handback>/HOWTO-PAGES.md`. Following only the handback docs, could someone with a new pairs file find every step, including `check_pairs.py`, the pick-one flags source, and the baseline retraining? Report anything missing or unclear.

## Known limits (not failures)
- The traffic test (`traffic_replay/`) has never run end to end: its SQL pull needs database access.
- The Docker-based training scripts (`run_model.sh`, `run_seed.sh`) cannot run in a sandbox without Docker access. If you can run Docker, optionally run `run_model.sh` for one seed of a small training file; it takes minutes.
- Functions in the original retrain files that have no docstring are intentionally left alone.
- A saved `baseline112_slices.csv` from an earlier date may differ from a fresh run by one pair (a later commit skips one unscorable pair).

## Report format
A table: test number, pass, fail or could not run (and the missing input if so), and one line of evidence. Then a short list of anything weird, stale, misleading or risky, ranked by how much it would bother the next owner of the ticket. Keep facility data out of the report.

End the report with a section **What I still need**: every input from the checklist above that was missing, which tests it left unrun, and what to send you so you can finish them.
