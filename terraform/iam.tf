# Lambda IAM Policy for S3 Write, read and list
data "aws_iam_policy_document" "s3_policy_doc" {
  statement {
    effect = "Allow"

      actions  = ["s3:PutObject",
                  "s3:GetObject",
                  "s3:ListBucket"
      ]

      resources = ["*"]
  }
}

# Creates IAM policy document 
# This policy gives the lambda function access to specific s3 actions stated above 

resource "aws_iam_policy" "s3_policy1" {
  name_prefix = "s3-ingested-policy"
  policy      = data.aws_iam_policy_document.s3_policy_doc.json
}


# Holds the actualy policy defined above 
# "policy" allows us to reference and generage the policy 
# This can then be used by multiple resources 


# Lambda IAM policy dov
data "aws_iam_policy_document" "trust_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# The block above is the trust policy that allows AWS lambda to assume the IAM ROLE created 


resource "aws_iam_role" "lambda_role" {
  name_prefix        = "role-lambda"
  assume_role_policy = data.aws_iam_policy_document.trust_policy.json
}

# Creates the IAM Role that the lambda function will assume, gives access to the s3 bucket with the specified permission 

#Attach
resource "aws_iam_role_policy_attachment" "lambda_s3_write_attachment" {
  role = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.s3_policy1.arn
}

# This resources attaches the s3 policy to the lambda function 
# Giving it permission to interact with the s3 bucket 


data "aws_iam_policy_document" "credentials_policy" {
  statement {
    effect = "Allow"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = ["arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:*"]
  }
}

# Policy doc for secretsmanager

resource "aws_iam_policy" "credentials" {
  name_prefix = "secrets_policy"
  policy      = data.aws_iam_policy_document.credentials_policy.json
}

# Policy for secretsmanager

resource "aws_iam_role_policy_attachment" "secrets_policy_role_attachment" {
  role = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.credentials.arn
}

# Attaching secretsmanager policy to our lambda role


  data "aws_iam_policy_document" "cw_document" {
    statement {
      effect="Allow"
      actions=["logs:CreateLogGroup"]
      resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
      #TODO: this statement should give permission to create Log Groups in your account
    }
  statement {


    effect="Allow"
    actions = ["logs:CreateLogStream", "logs:PutLogEvents"
]

    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*:*"
    ]
        #TODO: this statement should give permission to create Log Streams and put Log Events in the lambda's own Log Group

  }
}

resource "aws_iam_policy" "cw_policy" {
  name_prefix = "cw-policy-for-extract_lambda-"
  policy      = data.aws_iam_policy_document.cw_document.json
}

resource "aws_iam_role_policy_attachment" "lambda_cw_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.cw_policy.arn
}

resource "aws_cloudwatch_log_metric_filter" "ingestion_error_metric_filter" {
  name           = "ingestion_error_filter"
  pattern        ="\"ERROR\""
  log_group_name = aws_cloudwatch_log_group.cw_log_group.name

  metric_transformation {
    name      = "ingestion_error_filter"
    namespace = "Error"
    value     = "1"
  }
}

# Metric we are monitoring is lambda errors

resource "aws_cloudwatch_metric_alarm" "ingestionlambda_error_alarm" {
  alarm_name                = "LambdaIngestionErrorAlarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1 
  metric_name               = "ingestion_error_filter"
  namespace                 = "AWS/Lambda"
  period                    = 120
  statistic                 = "Sum"
  threshold                 = 2
  alarm_description         = "This metric monitors errors are logged"
  alarm_actions             = [aws_sns_topic.cw_alert_topic.arn]
  dimensions                = {FunctionName = aws_lambda_function.extract_lambda.function_name}

}



resource "aws_cloudwatch_log_group" "cw_log_group" {
  name =  "/aws/lambda/${aws_lambda_function.extract_lambda.function_name}" 
}


data "aws_iam_policy_document" "sns_policy_document" {
  statement {

    actions = ["sns:*"]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_policy" "sns_publish_policy" {
  name_prefix = "sns-publish-policy-"
  policy      = data.aws_iam_policy_document.sns_policy_document.json
}

resource "aws_iam_role_policy_attachment" "ingestion_sns_publish_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.sns_publish_policy.arn
}

# policy for processed data bucket


# #################### ====== TRANSFORM LAMBDA ======= #########################


resource "aws_cloudwatch_metric_alarm" "transform_lambda_error_alarm" {
  alarm_name                = "LambdaTransformErrorAlarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1 
  metric_name               = "transform_error_filter"
  namespace                 = "AWS/Lambda"
  period                    = 120
  statistic                 = "Sum"
  threshold                 = 2
  alarm_description         = "This metric monitors errors are logged"
  alarm_actions             = [aws_sns_topic.cw_alert_topic.arn]
  dimensions                = {FunctionName = aws_lambda_function.transform_lambda.function_name}

}


resource "aws_iam_policy" "extract_lambda_policy" {
  name   = "ExtractLambdaPolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # Permission to invoke transform_lambda on success
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
        Resource = [aws_lambda_function.transform_lambda.arn,aws_lambda_function.load_lambda.arn]
      },
      # Permission to publish to cw_alert_topic on failure
      {
        Effect = "Allow",
        Action = "sns:Publish",
        Resource = aws_sns_topic.cw_alert_topic.arn
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "extract_lambda_role_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.extract_lambda_policy.arn
}
