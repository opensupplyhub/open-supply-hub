resource "aws_sns_topic" "global" {
  name = "topic${local.short}GlobalNotifications"
}

#
# ALB application health (pages via SNS when the app is unhealthy independently
# of synthetic liveness). Used after OSDEV-2867 decoupled BetterStack from
# django-watchman DB checks — see doc/ops/monitoring.md.
#
resource "aws_cloudwatch_metric_alarm" "alb_target_5xx" {
  alarm_name          = "alarm${local.short}AppALBHTTPCodeTarget5XXCount"
  alarm_description   = "ALB target 5xx responses — application errors behind the load balancer"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = var.alb_target_5xx_alarm_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.app.arn_suffix
  }

  alarm_actions = [aws_sns_topic.global.arn]
  ok_actions    = [aws_sns_topic.global.arn]
}

resource "aws_cloudwatch_metric_alarm" "alb_target_response_time" {
  alarm_name          = "alarm${local.short}AppALBTargetResponseTime"
  alarm_description   = "ALB average target response time — elevated latency from app targets"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Average"
  threshold           = var.alb_target_response_time_alarm_threshold_seconds
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.app.arn_suffix
  }

  alarm_actions = [aws_sns_topic.global.arn]
  ok_actions    = [aws_sns_topic.global.arn]
}

resource "aws_cloudwatch_metric_alarm" "rds_database_connections" {
  alarm_name          = "alarm${local.short}DatabaseServerDatabaseConnections-${var.rds_database_identifier}"
  alarm_description   = "RDS DatabaseConnections — connection pressure on the primary Postgres instance"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "60"
  statistic           = "Average"
  threshold           = var.rds_database_connections_alarm_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = module.database_enc.id
  }

  alarm_actions = [aws_sns_topic.global.arn]
  ok_actions    = [aws_sns_topic.global.arn]
}
