# Lambda IAM Policy for S3 Write
data "aws_iam_policy_document" "s3_policy_doc" {
  statement {
    effect = "Allow"

      actions = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListObject"
      ]

      resources = [
         "${aws_s3_bucket.ingested_bucket.arn}/*"
        
      ]
  }
}
# creates I am policy document 
# this policy gives the lambda function access to specific s3 actions stated above 

resource "aws_iam_policy" "s3_policy1" {
  name_prefix = "s3-ingested-policy"
  policy      = data.aws_iam_policy_document.s3_policy_doc.json
}


## Holdes the actualy policy defined above 
## "policy" allows us to reference and generage the policy 
## this can then be used by multiple resources 


# Lambda IAM Role
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

## the block above is the trust policy that allows AWS lambda to assume the IAM ROLE created 


resource "aws_iam_role" "lambda_role" {
  name_prefix        = "role-lambda"
  assume_role_policy = data.aws_iam_policy_document.trust_policy.json
}

## creates the IAM Role that the lambda functgion will assume, gives access to the s3 bucket with the specified permission 

#Attach
resource "aws_iam_role_policy_attachment" "lambda_s3_write_attachment" {
  role = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.s3_policy1.arn
}

## This resources attaches the s3 policy to the lambda function 
## giving it permission to interact with the s3 bucket 


data "aws_iam_policy_document" "credentials_policy" {
  statement {
    effect = "Allow"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = ["arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:*"]
  }
}

## policy doc for secretsmanager

resource "aws_iam_policy" "credentials" {
  name_prefix = "secrets_policy"
  policy      = data.aws_iam_policy_document.credentials_policy.json
}

## policy for secretsmanager

resource "aws_iam_role_policy_attachment" "secrets_policy_role_attachment" {
  role = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.credentials.arn
}

## attaching secretsmanager policy to our lambda role


##### EVENTBRIDGE POLICY ######

# resource "aws_iam_role" "scheduler" {
#   name = "schedule-ingestion-role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Principal = {
#           Service = ["scheduler.amazonaws.com"]
#         }
#         Action = "sts:AssumeRole"
#       }
#     ]
#   })
# }

# resource "aws_iam_policy" "scheduler" {
#   name = "schedule-ingestion-policy"
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         # allow scheduler to execute the task
#         Effect = "Allow",
#         Action = [
#                 "scheduler:ListSchedules",
#                 "scheduler:GetSchedule",
#                 "scheduler:CreateSchedule",
#                 "scheduler:UpdateSchedule",
#                 "scheduler:DeleteSchedule"
#         ]
        
#         Resource = "*"
#       },
#       { # allow scheduler to set the IAM roles of your task
#         Effect = "Allow",
#         Action = [
#           "iam:PassRole"
#         ]
#         Resource = "arn:aws:iam::*:role/*"
#       },    ]
#   })
# }

# resource "aws_iam_role_policy_attachment" "scheduler" {
#   policy_arn = aws_iam_policy.scheduler.arn
#   role       = aws_iam_role.scheduler.name
# }

## CLOUDWATCH
data "aws_iam_policy_document" "cw_document" {
  
  statement {

    actions = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:CreateLogGroup"
]

    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*:*"
    ]
  }
}

resource "aws_iam_policy" "cw_policy" {
  name_prefix = "cw-policy-ingestion-lambda-"
  policy      = data.aws_iam_policy_document.cw_document.json
}

resource "aws_iam_role_policy_attachment" "lambda_cw_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.cw_policy.arn
}
#metric we are monitoring is lambda errors

resource "aws_cloudwatch_metric_alarm" "ingestionlambda_error_alarm" {
  alarm_name                = "lambdaingestionerroralarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1 # to be clarifyied 
  metric_name               = "errors"
  namespace                 = "AWS/Lambda"
  period                    = 60 # to be edited as per the period needed
  statistic                 = "Sum"
  threshold                 = 1
  alarm_description         = "This metric monitors errors in our ingestion lamnbda function"
  alarm_actions             = [aws_sns_topic.cw_alert_topic.arn]# sns topic name beeing lambda_alert
  dimensions                = {FunctionName = aws_lambda_function.extract_lambda.function_name}

}

resource "aws_cloudwatch_log_metric_filter" "ingestion_error_metric_filter" {
  name           = "ingestion_error_filter"
  pattern        ="\"ERROR\""
  log_group_name = aws_cloudwatch_log_group.cw_log_group.name

  metric_transformation {
    name      = "ingestion_error_filter"
    namespace = "ingestion_error_filter"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_group" "cw_log_group" {
  name =  "/aws/lambda/extract_lambda"
}

