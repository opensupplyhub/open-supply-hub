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
| `pgaudit.log` | `ddl,role` | `rds_pgaudit_log` | `pending-reboot` |

Both defaults live in `deployment/terraform/variables.tf` and are deliberately
not overridden per environment, so every environment audits the same statement
classes.

`ddl,role` records schema changes (`CREATE`/`ALTER`/`DROP` of tables, indexes,
functions) and privilege changes (`GRANT`, `REVOKE`, `CREATE`/`ALTER`/`DROP
ROLE`). It does **not** record `SELECT`, `INSERT`, `UPDATE`, or `DELETE`.
Adding `read` or `write` would multiply log volume on the ingestion path, so
change `rds_pgaudit_log` only with a deliberate decision about log cost.

`pg_stat_statements` is loaded by default on PostgreSQL 11 and later. It is
listed explicitly because setting `shared_preload_libraries` in a custom
parameter group replaces the family default outright, and omitting it would
silently disable query statistics.

## Rollout, per environment

`shared_preload_libraries` is a static PostgreSQL parameter. Terraform stages
the change, but RDS applies it only on the next reboot — and RDS never reboots
an instance on its own for a parameter change, not even during the maintenance
window. Every environment runs `rds_multi_az = false`, so the reboot is a hard
restart with roughly 30-120 seconds of downtime, not a failover. Schedule it.

1. **Apply Terraform.** After the deploy, both parameters show as
   `pending-reboot` on the parameter group, and the instance shows
   `pending-reboot` for its parameter group status. Nothing is being audited yet.

2. **Reboot the instance** during a low-traffic window:

   ```bash
   aws rds reboot-db-instance --db-instance-identifier opensupplyhub-enc-<env>
   aws rds wait db-instance-available --db-instance-identifier opensupplyhub-enc-<env>
   ```

3. **Create the extension.** `pgaudit` was added to the `install_db_exts`
   management command, which is idempotent:

   ```bash
   ./deployment/run_cli_task <Env> "install_db_exts"
   ```

   This must run *after* the reboot. Before the reboot the library is not
   loaded and `CREATE EXTENSION pgaudit` fails with `pgaudit must be loaded via
   shared_preload_libraries`; the command logs that error and still installs the
   other extensions, so a premature run is harmless but achieves nothing.

4. **Verify** (psql through the bastion, as the master user):

   ```sql
   SHOW shared_preload_libraries;   -- expect rdsutils,pg_stat_statements,pgaudit
   SHOW pgaudit.log;                -- expect ddl,role
   SELECT extname FROM pg_extension WHERE extname = 'pgaudit';
   ```

   Then re-run the Vanta test `aws-rds-pgaudit-enabled` and confirm the
   environment passes.

### A note on ordering

pgaudit's own documentation says `CREATE EXTENSION pgaudit` should be called
*before* `pgaudit.log` is set. On RDS that is not strictly achievable when both
parameters ship in one Terraform change: the library has to be loaded (reboot)
before the extension can be created, and the reboot activates `pgaudit.log` at
the same moment. The gap only affects object-level auditing (`pgaudit.role`),
which OS Hub does not use — session auditing of the `ddl` and `role` classes
works correctly.

If an auditor requires AWS's documented order exactly, split the rollout: set
`rds_pgaudit_log = "none"` in the environment's tfvars for the first apply,
reboot, run `install_db_exts`, then remove the override and apply again. This
costs a second reboot per environment.

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
