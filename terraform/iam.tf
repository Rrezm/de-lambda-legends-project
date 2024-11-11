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

resource "aws_iam_policy" "s3_policy1" {
  name_prefix = "s3-ingested-policy"
  policy      = data.aws_iam_policy_document.s3_policy_doc.json
}

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

resource "aws_iam_role" "lambda_role" {
  name_prefix        = "role-lambda"
  assume_role_policy = data.aws_iam_policy_document.trust_policy.json
}

#Attach
resource "aws_iam_role_policy_attachment" "lambda_s3_write_attachment" {
  role = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.s3_policy1.arn
}


