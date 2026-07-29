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

Alarms publish to `topic<ShortEnv>GlobalNotifications` (`aws_sns_topic.global`). Subscribe that topic to the on-call / ops destination used for pages.

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

Per-environment `rds_database_connections_alarm_threshold` values (from `LEAST(DBInstanceClassMemory/9531392, 5000)`):

| Env | Instance | max_connections | Threshold |
| --- | --- | ---: | ---: |
| Development | `db.t3.micro` | 112 | **90** |
| Staging | `db.t3.large` | 901 | **720** |
| Test | `db.t3.2xlarge` | 3604 | **2880** |
| Preprod / Production / RBA | `db.m6in.4xlarge` | 5000 (capped) | **4000** |

Also enable **Performance Insights** in the AWS console for query-level triage during saturation (not an SNS alarm).

### Application load balancer

| Alarm | Metric | Pages when |
| --- | --- | --- |
| `…AppALBHTTPCodeTarget5XXCount` | `HTTPCode_Target_5XX_Count` | Sum > `alb_target_5xx_alarm_threshold` (default **25**/min for 2 periods) |
| `…AppALBTargetResponseTime` | `TargetResponseTime` | Average > `alb_target_response_time_alarm_threshold_seconds` (default **2s** for 3 periods) |

### Memcached

| Alarm | Metric | Pages when |
| --- | --- | --- |
| `…MemcachedCacheClusterCPUUtilization` | `CPUUtilization` | Average > `ec_memcached_alarm_cpu_threshold_percent` |
| `…MemcachedCacheClusterFreeableMemory` | `FreeableMemory` | Average < `ec_memcached_alarm_memory_threshold_bytes` |

### ECS CPU (autoscaling)

`aws-ecs-service-autoscaling` raises/lowers desired count on ECS `CPUUtilization` high/low. Those alarms drive scaling policies; they are **not** wired to the global SNS topic unless `sns_topic_arn` is passed (currently omitted). Treat them as capacity signals, not pages.

## Suggested triage order

When BetterStack liveness is green but users report errors, or when RDS/ALB alarms fire:

1. ALB 5xx / response time — app or upstream dependency failures.
2. RDS CPU, disk queue, connections, free memory — compare with Performance Insights (tiles / `api_facilityindex`).
3. ECS service events and task restarts (console / `log…App`).

Long-term tile/search offload remains under [OSDEV-1575](https://opensupplyhub.atlassian.net/browse/OSDEV-1575).
