resource "aws_scheduler_schedule" "schedule_lambda"{
    name = "schedule-ingestion"

    flexible_time_window {
    mode = "OFF"
  }

  # schedule_expression = "cron(*/30 * * * ? *)"
  schedule_expression = "rate(30 minutes)"

  end_date = "2024-11-14T17:00:00Z"

  target{
    arn         = aws_lambda_function.extract_lambda.arn
    role_arn    = aws_iam_role.lambda_role.arn
  }
}

