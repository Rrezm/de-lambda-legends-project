data "archive_file" "lambda" {
  type             = "zip"
  output_file_mode = "0666"
  source_file      = "${path.module}/../src/1-EXTRACT/extract_data.py"
  output_path      = "${path.module}/../extract_data.zip"
}

## Team 1 is currently working on this
## Lambda python code, has to be zipped before uploading to aws

data "archive_file" "layer" {

  type             = "zip"
  output_file_mode = "0666"
  source_file      = "${path.module}/layer.zip"
  output_path      = "${path.module}/../layer.zip"
}
 ## Layer is necessary as it zips ibraries, modules, or packages that your Lambda function requires to run but that aren’t included in AWS Lambda by default.

resource "aws_lambda_layer_version" "lambda_layer" {
  layer_name          = "lambda_layer"
  compatible_runtimes = [var.python_runtime]
  s3_bucket           = aws_s3_bucket.ingested_bucket.bucket
  s3_key              = "layers/layer.zip"
}

resource "aws_lambda_function" "extract_lambda" {

  function_name = extract_lambda
  handler       = "..."  
  runtime       = "python 3.8"
  role          = aws_iam_role.lambda_role.arn
  s3_bucket     = aws_s3_bucket.lambda_code_bucket.bucket
  s3_key        = "ingestion_lambda/extract_data.zip"
  layers        = [aws_lambda_layer_version.requests_layer.arn]

}