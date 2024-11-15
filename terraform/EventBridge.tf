#this should set up a scheduler that will trigger the Lambda every 5 minutes
resource "aws_cloudwatch_event_rule" "scheduler" {
  name="schedule-for-extract_lambda"
  description="trigger the Lambda every 5 minutes"
  schedule_expression="cron(0/2 * * * ? *)"
}

#set lambda fxn as the targetof the cw event rule
#connects an event rule to a scheduled event rule with a target being Lambda function.
resource "aws_cloudwatch_event_target" "lambda_event_target" {
  target_id = "SendToLambda"
  rule      = aws_cloudwatch_event_rule.scheduler.name
  arn       = aws_lambda_function.extract_lambda.arn
}
#give cwpermissions to invoke lambda fxn whne the event rules triggers
resource "aws_lambda_permission" "permissions_to_allow_cloudwatch_to_invoke_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.extract_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduler.arn
}
resource "aws_sns_topic" "cw_alert_topic" {
  name = "CwEmailAlert"
}
resource "aws_sns_topic_subscription" "cw_email_subscription" {
  topic_arn = aws_sns_topic.cw_alert_topic.arn
  protocol  = "email"
  endpoint  = "mirriamb89@gmail.com"  #to be replaced
}