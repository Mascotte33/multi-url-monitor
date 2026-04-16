resource "aws_sns_topic" "logs" {
  name = "logs-topic"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.logs.arn
  protocol  = "email"
  endpoint  = var.alert_email

}

resource "aws_cloudwatch_log_group" "worker_logs" {
  name              = "/url-monitor/worker"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_metric_filter" "error_filter" {
  name           = "worker-error-filter"
  log_group_name = aws_cloudwatch_log_group.worker_logs.name
  pattern        = "ERROR"
  metric_transformation {
    name      = "WorkerErrorCount"
    namespace = "url-monitor"
    value     = 1
  }
}

resource "aws_cloudwatch_metric_alarm" "error_alarm" {
  alarm_name          = "worker-error-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "WorkerErrorCount"
  namespace           = "url-monitor"
  period              = 120
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "This metric monitors errors on S3"
  alarm_actions       = [aws_sns_topic.logs.arn]
}
