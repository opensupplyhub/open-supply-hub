# Facility index backfill

Targeted batch updates for denormalized columns on the `FacilityIndex` model.

## Purpose

Open Supply Hub stores search and display data in `FacilityIndex` (see `api.models.facility.facility_index.FacilityIndex`). Those rows are built from many PostgreSQL `index_*()` functions (see `src/django/sqls/0171_index_facilities.sql`).

When an `index_*()` function changes in a migration, you usually only need to refresh the affected column(s), not the entire index row.

### Why not `index_facilities_new`?

Historically, full reindexes ran via the `index_facilities_new` management command, which calls the `index_facilities()` stored procedure. That procedure recomputes **every** indexed column for **every** facility in one job.

As the number of production locations has grown into the millions, a full reindex can run for **hours**. Each facility triggers dozens of `index_*()` calls, so cost scales with `(locations) × (index functions)`.

This package provides a faster alternative: **batched, parallel backfills for specific field groups**, reusing the same `index_*()` SQL functions but only updating the columns that changed.

## Entry point

Single management command:

```bash
python manage.py backfill_facility_index --fields contributors
```

Common options:

```bash
# Parallel workers + batch size
python manage.py backfill_facility_index \
  --fields contributors \
  --parallel 10 \
  --batch-size 10000

# Dry run (row counts only)
python manage.py backfill_facility_index --fields contributors --dry-run

# Multiple field groups (run sequentially)
python manage.py backfill_facility_index --fields contributors,claim_info
```

### Post-deployment wiring (temporary)

When a release changes an `index_*()` function, **temporarily** add a `backfill_facility_index` call to `post_deployment` so the backfill runs automatically on deploy. **Remove that call once the release code freeze is complete and the release has been deployed everywhere** — `post_deployment` is not a permanent home for backfills.

Example wiring (remove after deploy):

```python
call_command(
    'backfill_facility_index',
    fields='contributors',
    parallel=backfill_parallel_worker_count(),
    batch_size=10000,
)
```

If environments differ in CLI memory, add a temporary `BACKFILL_PARALLEL_BY_ENVIRONMENT` map and `backfill_parallel_worker_count()` helper in `post_deployment.py`. Remove those helpers together with the backfill call.

```python
from django.conf import settings

# Each worker is a full Django subprocess (~150–200 MB RSS).
BACKFILL_PARALLEL_BY_ENVIRONMENT = {
    'Development': 2,
    'Test': 10,
    'Staging': 10,
    'Preprod': 10,
    'Production': 10,
    'Rba': 10,
}


def backfill_parallel_worker_count() -> int:
    return BACKFILL_PARALLEL_BY_ENVIRONMENT[settings.ENVIRONMENT]
```

## How it works

```
backfill_facility_index (orchestrator command)
        │
        ▼
BackfillOrchestrator (backfill_orchestrator.py)
        │
        ├── reads field group spec from specs.py
        └── spawn N backfill_facility_index_worker subprocesses (N = --parallel)
                │
                ▼
        BackfillWorker (backfill_worker.py)
              COUNT assigned rows
              loop: UPDATE batch via keyset pagination (id > last_id)
                    SET columns from index_*() expressions
                    COMMIT per batch
```

The worker command (`backfill_facility_index_worker`) is not intended for direct use in normal operations; the orchestrator invokes it with explicit CLI arguments (`--field`, `--worker-id`, `--workers`, `--batch-size`, `--result-file`).

### Parallelism

Workers partition rows with:

```sql
mod(abs(hashtext(id::text)), workers) = worker_id
```

Each worker processes disjoint id ranges using keyset pagination (`id > last_id ORDER BY id LIMIT batch_size`), so batches stay fast at scale.

### CLI memory and worker count

Each `--parallel` worker is a separate `manage.py` subprocess that bootstraps the full Django stack. The orchestrator process stays alive while workers run, so peak container memory is roughly:

```
(orchestrator + N workers) × ~150–200 MB per process
```

For example, **`--parallel 10` needs about 2 GB RSS** (11 processes). Row data is not held in Python — only Django startup dominates memory.

Choose `--parallel` to fit the CLI/ECS task memory limit (`cli_fargate_memory` in Terraform). If the task is killed with OOM, reduce `--parallel` before increasing batch size.

When a backfill is wired into `post_deployment`, worker count may be set per environment via a temporary `BACKFILL_PARALLEL_BY_ENVIRONMENT` map in `post_deployment.py` (remove with the backfill call). For example, **Development** may use **`--parallel 2`** when the CLI task has 1 GB memory and the database is small; larger environments may use **`--parallel 10`**.

For manual runs outside `post_deployment`, pass `--parallel` directly on the command line.

### Production observations (19 Jun 2026)

Reference run on **Production** RDS (`db.m6in.4xlarge` at the time) backfilling the **`contributors`** field group with **`--parallel 10`** and **`--batch-size 10000`**:

| Metric | Observed impact |
| --- | --- |
| Duration | ~**3.5 minutes** to complete |
| DB CPU | ~**+30%** while the job was running |
| DB connections | ~**+10** (one connection per parallel worker) |
| Environment availability | **No downtime** — the app remained available throughout |

Use this as a rough sizing guide when choosing `--parallel` on large environments. Higher parallelism finishes sooner but adds concurrent load on CPU and connection pools; monitor RDS during the first run after deploy.

### Field groups

Field groups are defined in `specs.py` as `FACILITY_INDEX_FIELD_SPECS`. Each group specifies:

| Key | Description |
| --- | --- |
| `columns` | Map of `FacilityIndex` field → SQL expression (usually calling an `index_*()` function) |
| `filter_sql` | Optional extra `WHERE` clause to skip rows that do not need updating |
| `from_clause` | Optional `FROM`/`JOIN` when expressions need `api_facility` columns (e.g. `location`, `name`) |
| `id_column` | Id column for pagination (default `afi.id`) |

Column expressions should match `index_facilities()` in `src/django/sqls/0171_index_facilities.sql` so backfill results stay consistent with a full reindex.

### Adding a new field group

1. Identify the changed `index_*()` function and target column(s) in `0171_index_facilities.sql`.
2. Add an entry to `FACILITY_INDEX_FIELD_SPECS` in `specs.py`.
3. If the expression needs facility attributes beyond `afi.id`, set `from_clause` to join `api_facility`.
4. Run locally:

   ```bash
   python manage.py backfill_facility_index --fields your_group --dry-run
   python manage.py backfill_facility_index --fields your_group --parallel 4
   ```

5. If it must run automatically on deploy, **temporarily** wire the group into `post_deployment`, then remove that call after the release code freeze is complete and the release has been deployed everywhere.

When a change affects related columns (e.g. `contributors` and `contributors_count`), define them in the **same** field group so one pass keeps data consistent.

## Keeping specs in sync

`FACILITY_INDEX_FIELD_SPECS` must stay aligned with the live index schema. Update it whenever:

- A column is **added, renamed, or removed** on `FacilityIndex`
- An **`index_*()` function** changes and you rely on targeted backfill instead of a full reindex
- **`index_facilities()`** gains new column expressions in `src/django/sqls`

Checklist for `FacilityIndex` changes:

1. Update `FacilityIndex` model and migration
2. Update `index_facilities()` / related `index_*()` SQL
3. Add or update the matching field group in `specs.py`
4. Run `backfill_facility_index --fields …` (or wire into `post_deployment`) after deploy

The model docstring on `FacilityIndex` also references this package as a reminder during code review.

## Package layout

| File | Role |
| --- | --- |
| `specs.py` | Field group registry and SQL builders |
| `backfill_orchestrator.py` | `BackfillOrchestrator` |
| `backfill_worker.py` | `BackfillWorker` |
| `utils.py` | Shared helpers (e.g. worker log labels) |
| `README.md` | This document |

| Command | Role |
| --- | --- |
| `backfill_facility_index` | Orchestrator CLI (`--fields`, `--parallel`, …) |
| `backfill_facility_index_worker` | Single hash partition; spawned by orchestrator |

## Related commands

| Command | Use when |
| --- | --- |
| `backfill_facility_index` | A migration changed one or more `index_*()` functions; refresh only those columns |
| `index_facilities_new` | Full rebuild of all index columns (small datasets, local dev, or rare full refresh) |
| `reindex_database` | Legacy wrapper around full database reindexing |
