#this should set up a scheduler that will trigger the Lambda every 2 minutes
resource "aws_cloudwatch_event_rule" "scheduler" {
  name="schedule-for-extract_lambda"
  description="trigger the Lambda every 2 minutes"
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
  principal     = "Lambda.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduler.arn
}

resource "aws_lambda_function_event_invoke_config" "example" {
  function_name = aws_lambda_function.extract_lambda.function_name

  destination_config {
    on_failure {
      destination =  aws_sns_topic.cw_alert_topic.arn
    }

    on_success {
      destination =aws_lambda_function.transform_lambda.arn
  }
}
}


resource "aws_lambda_permission" "permissions_to_allow_transform_lambda_to_be_triggered" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.transform_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_lambda_function.extract_lambda.arn
}
#our target should be asynchronous invocation
#make event rule for when it succeds,event target being TransformationLambda,setting  perms for lambda to inoke incase of incase of success
#another event rule for when it fails,event target being ssns topic, setting lambda permission to send sns incase of failuire
# resource "aws_cloudwatch_event_rule" "lambda_success_rule" {
#   name="lambda_success_rule"
#   description=" ingested lambda invokes transformation lambda once its succeeds"
#   event_pattern = 
# }
# event_pattern={
#   "source": ["aws.cloudformation"],
#   "detail-type": ["CloudFormation Resource Status Change"],
#   "detail": {
#     "status-details": {
#       "status": ["CREATE_COMPLETE"]
#     },
#     "resource-type": ["AWS::S3::Bucket", "AWS::SNS::Topic"]
#   }
# }