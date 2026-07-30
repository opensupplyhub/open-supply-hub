# Health checks and CloudWatch monitoring

Follow-up to [OSDEV-2867](https://opensupplyhub.atlassian.net/browse/OSDEV-2867) and the [Incident Report – April 21–22, 2026](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/1243414530/Incident+Report+-+April+21-22+2026).

## Application endpoint

| URL | Purpose | Touches Postgres / cache? |
| --- | --- | --- |
| `GET /health-check/` | **Liveness** — Django process is up and serving HTTP | No |

Response: HTTP 200, body `ok` (`text/plain`). No django-watchman database or cache checks.

`OriginSourceMiddleware` and `DarkVisitorsMiddleware` skip `/health-check/` so probes do not issue a session `SET` or call Dark Visitors.

Database and cache health are covered by CloudWatch (below), not by this URL.

### BetterStack (synthetic uptime)

Keep monitors on:

```text
https://<env-domain>/health-check/
```

Expect HTTP 200 and body `ok`. After deploy, update any monitor that still expects the old watchman JSON payload.

### ALB and ECS

Both use `/health-check/` for liveness (same URL as BetterStack).

## CloudWatch alarms (SNS)

Alarms publish to `topic<ShortEnv>GlobalNotifications` (`aws_sns_topic.global` in `deployment/terraform/alarms.tf`).

```text
CloudWatch Alarm → SNS (topic…GlobalNotifications) → AWS Chatbot → Slack
```

When `aws_chatbot_slack_team_id` and `aws_chatbot_slack_channel_id` are set (private [`ci-deployment`](https://github.com/opensupplyhub/ci-deployment) tfvars), Terraform creates an [AWS Chatbot](https://docs.aws.amazon.com/chatbot/latest/adminguide/slack-setup.html) Slack channel configuration that subscribes that topic so CloudWatch alarm state changes post to Slack. If either ID is empty, Terraform skips Chatbot (no Slack delivery).

### Slack setup (once per AWS account)

1. In the AWS Console for that account/region: **Amazon Q Developer in chat applications** (Chatbot) → **Configure client** → **Slack** → authorize the workspace.
2. In Slack, invite the **AWS Chatbot** / **Amazon Q** app to the alerts channel.
3. Copy:
   - **Workspace (team) ID** — Chatbot console → configured clients, or Slack workspace settings (starts with `T`).
   - **Channel ID** — Slack → channel details / copy link (starts with `C`).
4. Put both values in the private `ci-deployment` tfvars for that environment:
   - `aws_chatbot_slack_team_id`
   - `aws_chatbot_slack_channel_id`

| Resource | Purpose |
| --- | --- |
| `aws_iam_role.chatbot` | Role assumed by Chatbot (`chatbot.amazonaws.com`) |
| `CloudWatchReadOnlyAccess` on that role | Enrich Slack cards with metric / alarm detail |
| `aws_chatbot_slack_channel_configuration.global_alarms` | Binds Slack channel to `aws_sns_topic.global` |
| Guardrail `ReadOnlyAccess` | Limits what Chatbot can do from the channel |

After deploy with IDs set: SNS → topic `topic…GlobalNotifications` → Subscriptions should list the Chatbot endpoint. Force a test `ALARM` on an alarm wired to that topic, confirm Slack, then restore `OK`.

### RDS (primary Postgres)

Provisioned by `module.database_enc` ([terraform-aws-postgresql-rds](https://github.com/opensupplyhub/terraform-aws-postgresql-rds), including the OSDEV-2867 `DatabaseConnections` alarm):

| Alarm (name pattern) | Metric | Pages when |
| --- | --- | --- |
| `…DatabaseServerCPUUtilization-…` | `CPUUtilization` | Average > `rds_cpu_threshold_percent` (default **75%**, 300s) |
| `…DatabaseServerDiskQueueDepth-…` | `DiskQueueDepth` | Average > `rds_disk_queue_threshold` (default **10**, 60s) |
| `…DatabaseServerFreeStorageSpace-…` | `FreeStorageSpace` | Average < `rds_free_disk_threshold_bytes` (default **5 GB**) |
| `…DatabaseServerFreeableMemory-…` | `FreeableMemory` | Average < `rds_free_memory_threshold_bytes` (default **128 MB**) |
| `…DatabaseCPUCreditBalance-…` | `CPUCreditBalance` | Average < `rds_cpu_credit_balance_threshold` (default **30**; **db.t\*** only) |
| `…DatabaseServerDatabaseConnections-…` | `DatabaseConnections` | Average > `rds_database_connections_alarm_threshold` (~**80%** of instance `max_connections`; set per env) |

Per-environment `rds_database_connections_alarm_threshold` values (from `LEAST(DBInstanceClassMemory/9531392, 5000)`). Thresholds use **~80% of `max_connections`** so SNS pages while ~20% headroom remains — before new clients fail with “too many connections”:

| Env | Instance | max_connections | Threshold (~80%) |
| --- | --- | ---: | ---: |
| Development | `db.t3.micro` | 112 | **90** |
| Staging | `db.t3.large` | 901 | **720** |
| Test | `db.t3.2xlarge` | 3604 | **2880** |
| Preprod / Production / RBA | `db.m6in.4xlarge` | 5000 (capped) | **4000** |

Also enable **Performance Insights** in the AWS console for query-level triage during saturation (not an SNS alarm).

### Memcached

| Alarm | Metric | Pages when |
| --- | --- | --- |
| `…MemcachedCacheClusterCPUUtilization` | `CPUUtilization` | Average > `ec_memcached_alarm_cpu_threshold_percent` |
| `…MemcachedCacheClusterFreeableMemory` | `FreeableMemory` | Average < `ec_memcached_alarm_memory_threshold_bytes` |

### ECS CPU (autoscaling)

`aws-ecs-service-autoscaling` raises/lowers desired count on ECS `CPUUtilization` high/low. Those alarms drive scaling policies; they are **not** wired to the global SNS topic unless `sns_topic_arn` is passed (currently omitted). Treat them as capacity signals, not pages.

## Suggested triage order

When BetterStack liveness is green but users report errors, or when RDS alarms fire:

1. RDS CPU, disk queue, connections, free memory — compare with Performance Insights (tiles / `api_facilityindex`).
2. ECS service events and task restarts (console / `log…App`).
3. ALB access logs / target health in the AWS console for 5xx or latency patterns.

Long-term tile/search offload remains under [OSDEV-1575](https://opensupplyhub.atlassian.net/browse/OSDEV-1575).
