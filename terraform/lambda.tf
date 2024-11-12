data "archive_file" "lambda" {
  type             = "zip"
  output_file_mode = "0666"
  source_file      = "${path.module}/../src/EXTRACT/extract_data.py"
  output_path      = "${path.module}/../extract_data.zip"
}



resource "aws_lambda_function" "extract_lambda" {

  function_name = extract_lambda
  handler       = "..."  
  runtime       = "python 3.11"
  role          = aws_iam_role.lambda_role.arn
  s3_bucket     = aws_s3_bucket.lambda_code_bucket.bucket
  s3_key        = "ingestion_lambda/extract_data.zip"
  layers        = [aws_lambda_layer_version.dependencies.arn]
  timeout       = 10
  depends_on = [aws_s3_object.lambda_code, aws_s3_object.layer_code]
}