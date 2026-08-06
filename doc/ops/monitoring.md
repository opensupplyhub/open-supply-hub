# Health checks and CloudWatch monitoring

Follow-up to [OSDEV-2867](https://opensupplyhub.atlassian.net/browse/OSDEV-2867) and the [Incident Report – April 21–22, 2026](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/1243414530/Incident+Report+-+April+21-22+2026).

## Architecture overview

Monitoring is split by concern:

| Layer | Tool | What it answers |
| --- | --- | --- |
| **App liveness** | BetterStack (synthetic), ALB target health, ECS health checks | Is Django up and serving HTTP? |
| **Infrastructure** | CloudWatch metric alarms → SNS → AWS Chatbot → Slack | Are RDS / Memcached (and related infra) healthy? |

```text
BetterStack ──► GET /health-check/ ──► HTTP 200 "ok"   (app process only)

ALB / ECS   ──► GET /health-check/ ──► same liveness probe

CloudWatch  ──► RDS + Memcached metrics
            ──► SNS topic…GlobalNotifications
            ──► AWS Chatbot
            ──► Slack
```

`GET /health-check/` does **not** check Postgres or Memcached. Infra failure can leave BetterStack green while users still see errors — use CloudWatch / Slack for that path.

## Application endpoint (liveness)

| URL | Purpose | Touches Postgres / cache? |
| --- | --- | --- |
| `GET /health-check/` | **Liveness** — Django process is up and serving HTTP | No |

Response: HTTP 200, body `ok` (`text/plain`).

`OriginSourceMiddleware` and `DarkVisitorsMiddleware` skip `/health-check/` so probes do not issue a session `SET` or call Dark Visitors.

### BetterStack (synthetic uptime)

Keep monitors on:

```text
https://<env-domain>/health-check/
```

Expect HTTP 200 and body `ok`.

### ALB and ECS

Both use `/health-check/` for liveness (same URL as BetterStack).

## CloudWatch alarms (SNS → Slack)

Alarms publish to `topic<ShortEnv>GlobalNotifications` (`aws_sns_topic.global` in `deployment/terraform/alarms.tf`).

```text
CloudWatch Alarm → SNS (topic…GlobalNotifications) → AWS Chatbot → Slack
```

When `aws_chatbot_manage_channel_configuration = true`, Terraform creates an [AWS Chatbot](https://docs.aws.amazon.com/chatbot/latest/adminguide/slack-setup.html) Slack channel configuration that subscribes SNS topics so CloudWatch alarm state changes post to Slack. See `deployment/terraform/chatbot.tf`. Slack IDs come from [`ci-deployment`](https://github.com/opensupplyhub/ci-deployment) tfvars.

### Shared AWS account (one channel config)

AWS allows **only one** Chatbot Slack channel configuration per Slack channel **per AWS account**. Two groups share an account + channel:

**Dev / Test / Preprod** (shared AWS account):

| Env | `aws_chatbot_manage_channel_configuration` | Role |
| --- | --- | --- |
| Test | `true` (owner) | Creates the channel config; `sns_topic_arns` = Test SNS + optional sibling ARNs |
| Development / Preprod | `false` | Own SNS topic only; no Chatbot resources |

**Production / Staging / RBA** (shared AWS account):

| Env | `aws_chatbot_manage_channel_configuration` | Role |
| --- | --- | --- |
| Production | `true` (owner) | Creates the channel config; `sns_topic_arns` = Prod SNS + optional sibling ARNs |
| Staging / RBA | `false` | Own SNS topic only; no Chatbot resources |

Owner optional list `aws_chatbot_additional_sns_topic_arns` defaults to `[]` (safe for a new account / first env). After **stable** sibling SNS topics exist, add their ARNs in private `ci-deployment` tfvars for the owner env and re-apply.

Do **not** put ephemeral Preprod in that Terraform list. Chatbot accepts an SNS ARN even when the topic does not exist yet and does **not** create a subscription later when the topic appears. Preprod attach/detach is CI-owned:

| When | Workflow | Script |
| --- | --- | --- |
| After Preprod terraform apply | `deploy_to_aws.yml` | `./deployment/sync_chatbot_sns_topic attach` → Test Chatbot config `chatbotOpenSupplyHubTestGlobalAlarms` |
| Before Preprod terraform destroy | `destroy.yml` | `./deployment/sync_chatbot_sns_topic detach` |

`attach` remove-then-re-adds the ARN so a previously listed-but-unsubscribed topic is repaired. After a **Test** apply while Preprod is live, Terraform may drop the CI-attached Preprod ARN (desired state is Test + Dev only); re-run Preprod deploy (or the attach script) to restore Slack paging.

New AWS account, first env: leave manage `true` and additional ARNs empty — only that env’s SNS is attached. If ownership later moves between envs in the same account, apply the previous owner with manage `false` first (destroys its Chatbot resources), then apply the new owner.

### Slack setup (once per AWS account)

1. In the AWS Console for that account/region: **Amazon Q Developer in chat applications** (Chatbot) → **Configure client** → **Slack** → authorize the workspace.
2. In Slack, invite the **AWS Chatbot** / **Amazon Q** app to the alerts channel.
3. Copy:
   - **Workspace (team) ID** — Chatbot console → configured clients, or Slack workspace settings (starts with `T`).
   - **Channel ID** — Slack → channel details / copy link (starts with `C`).
4. Put both values in the private `ci-deployment` tfvars for the **owner** environment (`aws_chatbot_manage_channel_configuration = true`):
   - `aws_chatbot_slack_team_id`
   - `aws_chatbot_slack_channel_id`

| Resource | Purpose |
| --- | --- |
| `aws_iam_role.chatbot` | Role assumed by Chatbot (`chatbot.amazonaws.com`) — owner env only |
| `CloudWatchReadOnlyAccess` on that role | Enrich Slack cards with metric / alarm detail |
| `aws_chatbot_slack_channel_configuration.global_alarms` | Binds Slack channel to owner + additional SNS topics |
| Guardrail `ReadOnlyAccess` | Limits what Chatbot can do from the channel |

After deploy: SNS → topic `topic…GlobalNotifications` → Subscriptions should list the Chatbot endpoint (for every topic attached to the shared config). Force a test `ALARM` on an alarm wired to that topic, confirm Slack, then restore `OK`.

### RDS (primary Postgres)

Provisioned by `module.database_enc` in `deployment/terraform/database.tf` ([terraform-aws-postgresql-rds](https://github.com/opensupplyhub/terraform-aws-postgresql-rds) `3.3.0`, including the OSDEV-2867 `DatabaseConnections` alarm). All listed alarms use `alarm_actions` / `ok_actions` / `insufficient_data_actions` → `aws_sns_topic.global`.

| Alarm (name pattern) | Metric | Pages when |
| --- | --- | --- |
| `…DatabaseServerCPUUtilization-…` | `CPUUtilization` | Average > `rds_cpu_threshold_percent` (default **75%**, 300s) |
| `…DatabaseServerDiskQueueDepth-…` | `DiskQueueDepth` | Average > `rds_disk_queue_threshold` (default **10**, 60s) |
| `…DatabaseServerFreeStorageSpace-…` | `FreeStorageSpace` | Average < `rds_free_disk_threshold_bytes` (~**10%** of allocated storage; set per env) |
| `…DatabaseServerFreeableMemory-…` | `FreeableMemory` | Average < `rds_free_memory_threshold_bytes` (~**5%** of instance RAM; set per env) |
| `…DatabaseCPUCreditBalance-…` | `CPUCreditBalance` | Average < `rds_cpu_credit_balance_threshold` (default **30**; **db.t\*** only) |
| `…DatabaseServerDatabaseConnections-…` | `DatabaseConnections` | Average > `rds_database_connections_alarm_threshold` (~**80%** of instance `max_connections`; set per env) |

Per-environment free memory / free disk thresholds (~5% of RAM, ~10% of allocated storage):

| Env | Instance / RAM | FreeableMemory | Allocated storage | FreeStorageSpace |
| --- | --- | ---: | ---: | ---: |
| Development | `db.t3.micro` / 1 GiB | **128 MB** | 128 GB | **13 GB** |
| Staging | `db.t3.large` / 8 GiB | **400 MB** | 128 GB | **13 GB** |
| Test | `db.t3.2xlarge` / 32 GiB | **1.6 GB** | 400 GB | **40 GB** |
| Preprod / Production / RBA | `db.m6in.4xlarge` / 64 GiB | **3.2 GB** | 256 GB | **25 GB** |

Per-environment `rds_database_connections_alarm_threshold` values (from `LEAST(DBInstanceClassMemory/9531392, 5000)`). Thresholds use **~80% of `max_connections`** so SNS pages while ~20% headroom remains — before new clients fail with “too many connections”:

| Env | Instance | max_connections | Threshold (~80%) |
| --- | --- | ---: | ---: |
| Development | `db.t3.micro` | 112 | **90** |
| Staging | `db.t3.large` | 901 | **720** |
| Test | `db.t3.2xlarge` | 3604 | **2880** |
| Preprod / Production / RBA | `db.m6in.4xlarge` | 5000 (capped) | **4000** |


### ElastiCache (Memcached)

Defined in `deployment/terraform/cache.tf`. CloudWatch alarms page via the same global SNS topic (and thus Chatbot → Slack). The cluster also sets `notification_topic_arn` to that topic for ElastiCache engine/maintenance notifications.

All envs use `cache.t3.medium` (~3.09 GiB). CPU stays at the shared default:

| Alarm | Metric | Period | Pages when |
| --- | --- | ---: | --- |
| `alarm…MemcachedCacheClusterCPUUtilization` | `CPUUtilization` (`AWS/ElastiCache`) | 300s | Average > `ec_memcached_alarm_cpu_threshold_percent` (default **75%**) |
| `alarm…MemcachedCacheClusterFreeableMemory` | `FreeableMemory` (`AWS/ElastiCache`) | 60s | Average < `ec_memcached_alarm_memory_threshold_bytes` (default **500 MB** / `500000000`, ~16% of node RAM) |

Both alarms: `evaluation_periods = 1`; `alarm_actions` / `ok_actions` / `insufficient_data_actions` → `aws_sns_topic.global`.

### ECS CPU (autoscaling)

`aws-ecs-service-autoscaling` raises/lowers desired count on ECS `CPUUtilization` high/low. Those alarms drive scaling policies; they are **not** wired to the global SNS topic unless `sns_topic_arn` is passed (currently omitted). Treat them as capacity signals, not pages.

## Suggested triage order

When BetterStack liveness is green but users report errors, or when RDS / Memcached alarms fire:

1. RDS CPU, disk queue, connections, free memory — compare with Performance Insights (tiles / `api_facilityindex`).
2. Memcached CPU and freeable memory (CloudWatch / Slack).
3. ECS service events and task restarts (console / `log…App`).
4. ALB access logs / target health in the AWS console for 5xx or latency patterns.

Long-term tile/search offload remains under [OSDEV-1575](https://opensupplyhub.atlassian.net/browse/OSDEV-1575).
