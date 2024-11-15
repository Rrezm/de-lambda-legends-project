resource "aws_sns_topic" "cw_alert_topic" {
  name = "CwEmailAlert"
}
resource "aws_sns_topic_subscription" "cw_email_subscription" {
  topic_arn = aws_sns_topic.cw_alert_topic.arn
  protocol  = "email"
  endpoint  = "joshkjman@hotmail.com"  #to be replaced
}