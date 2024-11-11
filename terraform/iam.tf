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