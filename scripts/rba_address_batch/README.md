# Address batch tool

Bulk-apply address corrections to production locations on a private
instance and make them the location's primary address.

## Why this tool exists

Submitting an address to Open Supply Hub does not change what a production
location displays. A submission is a *contribution*, and one contribution
has to be **promoted** before its name and address become the location's
primary values. Through the interface that is four operations per record,
which does not scale to a cleanup of any size.

This tool performs those steps for every row of a CSV, keeps a journal so
an interrupted run can be resumed, and writes a report for a human to
check before the batch is treated as done.

## Before you start

> **Do not run this against an instance that receives the one-way sync
> from Open Supply Hub until promotion re-assertion is deployed there.**
> On such an instance the sync overwrites every synced field of a shared
> location, including the record of which contribution is primary. A
> promotion this tool applies is therefore silently undone the next time
> the public record changes — there is no schedule to it, so a batch can
> look entirely correct for days and then decay. The `reassert_rba_promotions`
> management command restores promotions after each sync and must be in
> place first. If you are not certain it is deployed, ask the Open Supply
> Hub team before running a batch rather than after.

You need four things. The first three are one-time setup.

1. **A superuser account on the instance.** Both the approval and the
   promotion steps are restricted to superusers. A normal contributor
   account can submit, but cannot approve or promote.
2. **An API token for that account**, from the account's settings page.
3. **API access enabled for the account's contributor.** API calls are
   rate-limited per contributor and an account with no limit record
   configured will be refused. If calls fail with a limit or permission
   error before anything else happens, this is the likely cause — ask the
   Open Supply Hub team to configure it.
4. **The instance's base URL.**

Then install the one dependency:

```bash
python3 -m venv .venv
.venv/bin/pip install requests
```

## Configuration

Three environment variables. Nothing is read from a file, and the token is
never written to disk by this tool.

```bash
export RBA_BASE_URL="https://your-instance-host"
export RBA_TOKEN="your-api-token"
export RBA_CONTRIBUTOR_ID="123"   # the numeric contributor id of the account
```

The tool refuses to run against the public Open Supply Hub instance.
Promoting one contributor's submissions in bulk there would override other
contributors' data, so the check is in the code rather than left to
convention.

## Input file

A CSV with a header row. Required columns:

| Column | Meaning |
| --- | --- |
| `os_id` | the OS ID of the production location to correct |
| `name` | the name to submit |
| `address` | the corrected address |
| `country` | country name or code |

Optional but **strongly recommended**:

| Column | Meaning |
| --- | --- |
| `lat` | latitude |
| `lng` | longitude |

Submitted addresses are geocoded on the server, and a submission whose
address cannot be geocoded is **rejected**. Supplying explicit coordinates
skips geocoding entirely, so including `lat` and `lng` removes the most
common cause of failed rows. If your source data has coordinates, use
them.

A location may appear on more than one row. Rows for the same location are
processed in file order, so the last one wins that location's primary
address. The dry run tells you when this happens.

## Running it

**Always dry run first.** It is read-only — it creates and changes
nothing. It confirms your token is a superuser (approving and promoting
both require one, and a plain authenticated token would get all the way
to the approve step before failing), and that every location in the file
exists.

```bash
.venv/bin/python rba_address_batch.py updates.csv --dry-run
```

Fix anything it reports as a PROBLEM before continuing. Then:

```bash
.venv/bin/python rba_address_batch.py updates.csv --execute
```

Roughly a thousand records takes a bit under two hours — it is four calls
per record and deliberately paced so the batch does not degrade the
instance for its other users.

## Afterwards: read the report

`verification_report.csv` has one row per record, across **all** runs —
it is rebuilt from the journal each time, so resuming an interrupted
batch still gives you a report covering everything.

| Column | Meaning |
| --- | --- |
| `os_id` | the location |
| `submitted_address` | what the file asked for |
| `previous_primary_address` | what the location showed before the run |
| `resulting_primary_address` | what it shows now |
| `status` | `OK`, `CHECK …`, `FAILED …`, or `INCOMPLETE …` |

`CHECK unchanged` means the primary address is byte-identical to what it
was before the run, which usually means the promotion did not take.

`CHECK applied but not read back` means the opposite of a failure: the
changes went through, and only the confirming read afterwards failed.
The record is finished and will **not** be repeated on a later run —
repeating it would submit the address a second time for a location that
is already correct. Look at these in the dashboard to confirm them.

`FAILED` rows are safe to re-run. `INCOMPLETE` rows are records a run
was in the middle of when it was killed outright, so it never got to
write down how they ended; the status says which step they reached.
Re-running the same input file picks both up where they stopped.

**The submitted and resulting addresses will not match character for
character, and that is normal.** Addresses are cleaned and standardised
when they are ingested — which is why the report compares against the
*previous* value rather than against what you submitted. The report
exists so a person can confirm the results are *right*, which is a
judgement a script cannot make. Do not treat the batch as complete until
someone has read it.

## If a run is interrupted

Just run the same command again. Every step of every record is recorded
in `batch_journal.jsonl`. Completed records are skipped, and a record
that got part of the way through **continues from where it stopped**
rather than starting over — if its address was already submitted, the
re-run approves that submission instead of making a second one.

That matters because the steps are not undoable. Starting a half-done
record again would leave its first submission sitting in the moderation
queue unapproved forever, and would promote the address twice.

**You can safely edit the CSV between runs** — delete rows that already
applied, or correct one that failed. Records are tracked by their content,
not their position in the file, so shifting the rows around does not
cause anything to be re-applied. Correcting a row's address makes it a
new record, which is what correcting it means.

Two things the tool will not decide for you:

- Resubmitting an **identical** address for the same location within 15
  minutes is rejected as a duplicate request, reported distinctly from a
  real failure. It means the earlier submission exists on the instance.
  If the run died before it could write down that submission's id, the
  tool cannot reach it: approve and promote it from the moderation queue
  by hand, or wait out the window and re-run to submit it afresh.
- If a record's moderation event is **no longer pending**, the run stops
  that record and says so. An interrupted run may already have approved
  it — leaving only the promotion outstanding — or a moderator may have
  rejected it. Those look the same from here, and the tool does not
  guess, because guessing wrong promotes an unrelated contribution over
  the location. Open the event in the moderation queue and finish or
  drop that record by hand.

If the instance rate-limits the run, the tool waits and retries rather
than failing those records — you will see `rate limited, waiting Ns`
messages. That is normal on a long batch and needs no action.

## While the batch runs

Avoid editing the same locations through the interface, and do not run two
batches at once. After approving a submission the tool has to work out
which contribution it just created, and it does that by taking your
newest one for that location — which is only reliable if nothing else is
writing to it at the same time.

This is a temporary limitation. Once the approval response reports the
contribution it created (OSDEV-3424), the tool uses that instead and the
caveat goes away — the tool already prefers the server's answer whenever
it is present, so no change here is needed when that ships.

## Verifying results yourself

Check a location through its profile page or the legacy facility endpoint,
which reflect a promotion immediately. Do **not** check through the
`/api/v1/` search endpoints — those read a search index that lags by an
indexing cycle, so a correct promotion can look like a failure for several
minutes.

## Tests

```bash
python -m unittest test_rba_address_batch -v
```

Covers the host guard, submission payload construction, the duplicate
window, match resolution, rate-limit backoff, row grouping, and the resume
path in detail: that a record already promoted repeats none of its writes,
that one already submitted is approved rather than submitted again, and
that a record whose changes landed but could not be read back is finished
rather than retried. The network calls themselves are mocked; there is no
test that talks to a real instance.
