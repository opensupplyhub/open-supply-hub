# Database activity auditing (pgaudit)

Every OS Hub environment runs a single-instance Amazon RDS for PostgreSQL 16
database (`opensupplyhub-enc-<env>`), provisioned by the `database_enc` module
in `deployment/terraform/database.tf`. There is no Aurora cluster in any
environment.

SOC 2 requires that database activity be auditable. This is provided by the
[pgaudit](https://github.com/pgaudit/pgaudit) extension, tracked in
[OSDEV-2997](https://opensupplyhub.atlassian.net/browse/OSDEV-2997) and checked
by the Vanta test `aws-rds-pgaudit-enabled`, which reads the DB parameter group
through the AWS API.

## What Terraform configures

`aws_db_parameter_group.default` in `deployment/terraform/database.tf` sets two
parameters:

| Parameter | Value | Variable | Apply method |
| --- | --- | --- | --- |
| `shared_preload_libraries` | `pg_stat_statements,pgaudit` | `rds_shared_preload_libraries` | `pending-reboot` |
| `pgaudit.log` | `none` (phase 1) → `ddl,role` (phase 2, [OSDEV-3236](https://opensupplyhub.atlassian.net/browse/OSDEV-3236)) | `rds_pgaudit_log` | `pending-reboot` |

Both defaults live in `deployment/terraform/variables.tf` and are not
overridden per environment, so every environment audits the same statement
classes. Both variables carry `validation` blocks: neither `pgaudit` nor
`pg_stat_statements` can be dropped from `shared_preload_libraries`, and
`pgaudit.log` only accepts real pgaudit classes and rejects `none` combined
with anything else.

`rds_pgaudit_log` ships as `none` and is flipped to `ddl,role` by
[OSDEV-3236](https://opensupplyhub.atlassian.net/browse/OSDEV-3236). That split
is not a preference — see Rollout below. Until OSDEV-3236 ships, the Vanta test
`aws-rds-pgaudit-enabled` still fails.

Once phase 2 lands, `ddl,role` records schema changes (`CREATE`/`ALTER`/`DROP` of tables, indexes,
functions) and privilege changes (`GRANT`, `REVOKE`, `CREATE`/`ALTER`/`DROP
ROLE`). It does **not** record `SELECT`, `INSERT`, `UPDATE`, or `DELETE`.
Adding `read` or `write` would multiply log volume on the ingestion path, so
change `rds_pgaudit_log` only with a deliberate decision about log cost.

`pg_stat_statements` is loaded by default on PostgreSQL 11 and later. It is
listed explicitly because setting `shared_preload_libraries` in a custom
parameter group replaces the family default outright, and omitting it would
silently disable query statistics.

## Rollout, per environment

The rollout has two phases, and the order matters. pgaudit's documentation is
explicit:

> `CREATE EXTENSION pgaudit` must be called before `pgaudit.log` is set to
> ensure proper pgaudit functionality. The extension installs event triggers
> which add additional auditing for DDL. pgAudit will work without the
> extension installed but DDL statements will not have information about the
> object type and name.

Because we audit the `ddl` class, that is not a cosmetic gap: DDL records
written before the extension exists lack `OBJECT_TYPE` and `OBJECT_NAME`, so
the log would show that a schema change happened but not what it touched. The
extension cannot be created before the library is loaded, and the library only
loads on reboot — so `pgaudit.log` stays `none` across that first reboot. That
is why `rds_pgaudit_log` defaults to `none` in the committed configuration
rather than relying on anyone remembering to stage it.

`shared_preload_libraries` is a static PostgreSQL parameter. Terraform stages
the change, but RDS applies it only on the next reboot, and RDS never reboots
an instance on its own for a parameter change — not even during the maintenance
window. Every environment runs `rds_multi_az = false`, so each reboot is a hard
restart with roughly 30-120 seconds of downtime, not a failover.

### Phase 1 — load the library, create the extension (this release)

1. Apply Terraform. Both parameters land on the parameter group as
   `pending-reboot`, with `pgaudit.log` at `none`.

2. Reboot the instance:

   ```bash
   aws rds reboot-db-instance --db-instance-identifier opensupplyhub-enc-<env>
   aws rds wait db-instance-available --db-instance-identifier opensupplyhub-enc-<env>
   ```

   pgaudit is now loaded, with session auditing off.

3. Create the extension. `pgaudit` is part of the idempotent `install_db_exts`
   management command, which exits non-zero if any extension fails — so a green
   run is the completion signal:

   ```bash
   ./deployment/run_cli_task <Env> "install_db_exts"
   ```

4. Confirm the extension exists before calling phase 1 done:

   ```sql
   SHOW shared_preload_libraries;   -- expect rdsutils,pg_stat_statements,pgaudit
   SHOW pgaudit.log;                -- expect none
   SELECT extname FROM pg_extension WHERE extname = 'pgaudit';
   ```

Run phase 1 on Development, then Staging, before Production.

### Phase 2 — turn auditing on ([OSDEV-3236](https://opensupplyhub.atlassian.net/browse/OSDEV-3236))

Tracked separately, because it must not ship until phase 1 has completed in the
environment being changed. It flips the `rds_pgaudit_log` default to `ddl,role`,
which is applied by another Terraform apply and another reboot, then verified by
running a harmless DDL statement and confirming the audit record carries a
populated `OBJECT_TYPE` and `OBJECT_NAME`. Full acceptance criteria are on that
ticket.

> If the `pgaudit` extension is ever dropped and needs recreating, set
> `pgaudit.log` back to `none` first — pgaudit raises an error otherwise. That
> is the same ordering constraint as this rollout.

## Where the audit records go

pgaudit writes to the standard PostgreSQL log, which on RDS means the
instance's local log files. **These logs are not currently exported to
CloudWatch Logs** — `deployment/terraform/database.tf` does not pass
`cloudwatch_logs_exports` to the `database_enc` module, so RDS applies its own
short retention and the records are not centrally searchable or retained.

Enabling `enabled_cloudwatch_logs_exports = ["postgresql"]` is out of scope for
OSDEV-2997 and carries its own ingestion cost, but any control that requires
retaining audit records for a fixed period will need it. This also applies to
the connection, lock-wait, and slow-query logging the parameter group already
enables.

## What is not configured

- `pgaudit.role` — object-level auditing keyed to a master role. Not set, so no
  `rds_pgaudit` role is required in any environment.
- `read` / `write` statement classes — excluded on log-volume grounds.
- CloudWatch Logs export — see above.
- pgaudit is not available in the local `postgres:16` image used by
  `docker-compose`, so `install_db_exts` fails on that one extension (and
  therefore exits non-zero) outside AWS. The command is not part of local
  setup.
