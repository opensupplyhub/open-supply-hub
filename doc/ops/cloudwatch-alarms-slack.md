# CloudWatch alarms → Slack (AWS Chatbot)

CloudWatch alarms publish to the per-environment SNS topic
`topic<ShortEnv>GlobalNotifications` (`aws_sns_topic.global` in
`deployment/terraform/alarms.tf`).

When Slack IDs are set, Terraform creates an [AWS Chatbot](https://docs.aws.amazon.com/chatbot/latest/adminguide/slack-setup.html)
Slack channel configuration that subscribes that topic and posts alarm
state changes into Slack.

## Flow

```text
CloudWatch Alarm → SNS (topic…GlobalNotifications) → AWS Chatbot → Slack channel
```

## One-time setup (per AWS account)

1. In the AWS Console for that account/region: **Amazon Q Developer in chat applications** (Chatbot) → **Configure client** → **Slack** → authorize the workspace.
2. In Slack, invite the **AWS Chatbot** / **Amazon Q** app to the alerts channel.
3. Copy:
   - **Workspace (team) ID** — Chatbot console → configured clients, or Slack workspace settings (starts with `T`).
   - **Channel ID** — Slack → channel details / copy link (starts with `C`).
4. Put both values in the private [`ci-deployment`](https://github.com/opensupplyhub/ci-deployment) tfvars for that environment:
   - `aws_chatbot_slack_team_id`
   - `aws_chatbot_slack_channel_id`

If either value is empty, Terraform skips creating Chatbot resources (no Slack notifications).

## Terraform resources

| Resource | Purpose |
| --- | --- |
| `aws_iam_role.chatbot` | Role assumed by Chatbot (`chatbot.amazonaws.com`) |
| `CloudWatchReadOnlyAccess` on that role | Enrich Slack cards with metric / alarm detail |
| `aws_chatbot_slack_channel_configuration.global_alarms` | Binds Slack channel to `aws_sns_topic.global` |
| Guardrail `ReadOnlyAccess` | Limits what Chatbot can do from the channel |

## Verify after deploy

1. SNS → topic `topic…GlobalNotifications` → Subscriptions should list the Chatbot endpoint (no longer empty).
2. CloudWatch → pick an alarm wired to that topic → temporarily set state to `ALARM` (or lower a threshold) and confirm the Slack message.
3. Return the alarm to `OK`.
