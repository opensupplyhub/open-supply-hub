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

CloudWatch  ──► RDS + Memcached + Lambda metrics
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

When `aws_chatbot_manage_channel_configuration = true`, Terraform creates an [AWS Chatbot](https://docs.aws.amazon.com/chatbot/latest/adminguide/slack-setup.html) Slack channel configuration that subscribes SNS topics so CloudWatch alarm state changes post to Slack. See `deployment/terraform/chatbot.tf`. Slack workspace and channel IDs are read from the owner env’s SM secret (`oshub/<owner>/aws-chatbot-slack-config`, referenced by `aws_chatbot_slack_config_secret_name` in public tfvars — Test and Production today) as JSON `{"team_id":"…","channel_id":"…"}`.

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

Owner optional list `aws_chatbot_additional_sns_topic_arns` defaults to `[]` (safe for a new account / first env). After **stable** sibling SNS topics exist, update the owner env’s SM secret (`oshub/<owner>/aws-chatbot-additional-sns-topic-arns`, referenced by `aws_chatbot_additional_sns_topic_arns_secret_name` in public tfvars — Test and Production today) via the `sm-secrets-cli` repo or any other method, then re-apply the owner env.

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
4. Seed the owner env’s SM secret (`aws_chatbot_slack_config_secret_name`, e.g. `oshub/test/aws-chatbot-slack-config` or `oshub/production/aws-chatbot-slack-config`) via the `sm-secrets-cli` repo or any other method with JSON:
   ```json
   {"team_id": "T…", "channel_id": "C…"}
   ```

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

### Lambda (all functions)

Defined in `deployment/terraform/alarms.tf`. One **un-dimensioned** alarm on the `AWS/Lambda` `Errors` metric covers every Lambda function in the environment's region at once — there is no `FunctionName` dimension, so functions added later are covered the moment they are created.

| Alarm | Metric | Period | Pages when |
| --- | --- | ---: | --- |
| `alarm…LambdaErrors` | `Errors` (`AWS/Lambda`, no `FunctionName` dimension — covers all functions) | 300s | Sum > `lambda_errors_alarm_threshold` (default **0**, i.e. any error) |

`evaluation_periods = 1`; `alarm_actions` / `ok_actions` → `aws_sns_topic.global`. `treat_missing_data = notBreaching`: an idle environment publishes no datapoints, which is normal, so there are no insufficient-data pages.

Functions in scope (`local.short` = e.g. `OpenSupplyHubProduction`):

| Function | Defined in | Covered |
| --- | --- | --- |
| `func…AlertBatchFailures` | `lambda.tf` | Yes |
| `func…AlertStepFunctionsFailures` | `lambda.tf` | Yes |
| `func…ContribotFetchLists` | `contribot_lambda.tf` | Yes |
| `func…ContribotProcessList` | `contribot_lambda.tf` | Yes |
| `func…ContribotNotify` | `contribot_lambda.tf` | Yes |
| `func…ContribotRetryFailedLists` | `contribot_lambda.tf` | Yes |
| `func…NlbTargetsRegistrar` | `database-private-link-provider/lambda-nlb-registrar.tf` | Yes, where that module is applied |
| `func…RedirectToS3origin` | `lambda.tf` (Lambda@Edge) | Partial — see below |
| `func…AddSecurityHeaders` | `lambda.tf` (Lambda@Edge) | Partial — see below |

The trade-off of a single un-dimensioned alarm: Slack reports that *a* Lambda errored, not which one. To identify it, open the `AWS/Lambda` `Errors` metric broken down by `FunctionName` for the alarm window, or the relevant `/aws/lambda/func…` log group.

**Lambda@Edge caveat.** `RedirectToS3origin` and `AddSecurityHeaders` are created in `us-east-1` (the `aws.certificates` provider), but CloudFront executes them at edge locations worldwide and [their CloudWatch metrics and logs are published in the AWS Region closest to where the function executed](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-edge-testing-debugging.html), not centrally. This alarm therefore only sees edge errors for executions that land in `var.aws_region`.

Closing that gap is not a matter of adding a dimension, because **a CloudWatch alarm can only publish to an SNS topic in its own region** — an alarm in `us-east-1` (or any other edge region) cannot use `aws_sns_topic.global`. The options, if edge coverage becomes a requirement:

1. Create a second SNS topic in `us-east-1` and add its ARN to the Chatbot channel configuration (Chatbot accepts topics from multiple regions), then add a matching un-dimensioned alarm there. Covers `us-east-1` edge executions and anything else in that region.
2. Use CloudFront's own `LambdaExecutionError` / `LambdaValidationError` metrics, which are global and reported in `us-east-1`. These are CloudFront **additional metrics** and must be enabled per distribution at extra cost.

Neither is in place today; both edge functions are thin (a redirect and a response-header rewrite) and their failures surface as CloudFront 5xx.

### ECS CPU (autoscaling)

`aws-ecs-service-autoscaling` raises/lowers desired count on ECS `CPUUtilization` high/low. Those alarms drive scaling policies; they are **not** wired to the global SNS topic unless `sns_topic_arn` is passed (currently omitted). Treat them as capacity signals, not pages.

### Bedrock (SLC submission quality check)

Defined in `deployment/terraform/alarms.tf`. The SLC submission quality check makes one Bedrock (Claude Haiku) call per new SLC submission — organic volume is tens of calls per **week**. There is deliberately no in-app cap on these calls: per-user volume is bounded by the endpoint's `DataUploadThrottle` (30/minute), and runaway volume (a frontend retry loop, scripted submissions across accounts) is caught by monitoring instead, accepting a bounded-spend risk rather than risking the check or submissions being silently degraded by a cap.

| Alarm | Metric | Period | Pages when |
| --- | --- | ---: | --- |
| `alarm…BedrockInvocations` | `Invocations` (`AWS/Bedrock`, no `ModelId` dimension — covers all models/callers) | 3600s | Sum > `bedrock_invocations_alarm_hourly_threshold` (default **100/hour**, orders of magnitude above organic volume) |

`treat_missing_data = notBreaching`: zero calls in an hour is the normal state, so no insufficient-data pages. Bedrock metrics land in the calling region, so the alarm only sees traffic where the app's `BEDROCK_AWS_REGION` matches the env's `aws_region`.

A monthly AWS Budget on Bedrock spend (`budget…Bedrock`, limit `bedrock_cost_budget_monthly_limit_usd`, default **$25**) alerts at 80% actual and 100% forecasted through the same SNS → Chatbot → Slack path. Budgets are account-wide, so only the account-owner envs create one (`manage_bedrock_cost_budget = true` — Test and Production today, mirroring the Chatbot ownership pattern).

The Django app also logs per-call token usage (`Submission quality check tokens: input=… output=…`) to CloudWatch Logs for verifying actual consumption against expectations (~640 tokens/call).

## Suggested triage order

When BetterStack liveness is green but users report errors, or when RDS / Memcached alarms fire:

1. RDS CPU, disk queue, connections, free memory — compare with Performance Insights (tiles / `api_facilityindex`).
2. Memcached CPU and freeable memory (CloudWatch / Slack).
3. ECS service events and task restarts (console / `log…App`).
4. ALB access logs / target health in the AWS console for 5xx or latency patterns.

Long-term tile/search offload remains under [OSDEV-1575](https://opensupplyhub.atlassian.net/browse/OSDEV-1575).
