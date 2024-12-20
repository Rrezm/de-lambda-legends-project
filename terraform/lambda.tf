###### Ingestion LAMBDA ######

data "archive_file" "lambda" {
  type             = "zip"
  output_file_mode = "0666"
  source_file      = "${path.module}/../src/EXTRACT/lambda_extract.py"
  output_path      = "${path.module}/../extract_data.zip"
}


resource "aws_lambda_function" "extract_lambda" {
  function_name = "extract_lambda"
  handler       = "lambda_extract.read_all_tables"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_role.arn
  s3_bucket     = aws_s3_bucket.lambda_code_bucket.bucket
  s3_key        = "ingestion_lambda/extract_data.zip"
  layers        = [aws_lambda_layer_version.lambda_layer.arn]
  timeout       = 100
  depends_on = [aws_s3_object.lambda_code, aws_s3_object.layer_code]
  source_code_hash = data.archive_file.lambda.output_base64sha256
}


###### Transformation LAMBDA ######

data "archive_file" "transform_lambda" {
  type             = "zip"
  output_file_mode = "0666"
  source_file      = "${path.module}/../src/TRANSFORM/lambda_transform.py"
  output_path      = "${path.module}/../lambda_transform.zip"
}


resource "aws_lambda_function" "transform_lambda" {
  function_name = "transform_lambda"
  handler       = "lambda_transform.lambda_handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_role.arn
  s3_bucket     = aws_s3_bucket.processed_lambda_code_bucket.bucket
  s3_key        = "processed_lambda_code_bucket/lambda_transform.zip" #if doesn't work switch to transform_lambda.zip
  # Pandas is too big to be stored in a dependencies layer so we use a managed layer for pandas
  layers        = ["arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python311:18"]
  timeout       = 900
  memory_size   = 1000
  depends_on = [aws_s3_object.transform_lambda_code]
  source_code_hash = data.archive_file.transform_lambda.output_base64sha256
}


###### Load LAMBDA #######

data "archive_file" "load_lambda" {
  type             = "zip"
  output_file_mode = "0666"
  source_file      = "${path.module}/../src/LOAD/lambda_load.py" #
  output_path      = "${path.module}/../lambda_load.zip"
}


resource "aws_lambda_function" "load_lambda" {
  function_name = "load_lambda"
  handler       = "lambda_load.input_data_psql" #
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_role.arn
  s3_bucket     = aws_s3_bucket.load_lambda_code_bucket.bucket
  s3_key        = "load_lambda_code_bucket/lambda_load.zip" 
  layers        = ["arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python311:18",aws_lambda_layer_version.lambda_layer.arn]
  timeout       = 900
  memory_size   = 1000
  depends_on = [aws_s3_object.load_lambda_code]
  source_code_hash = data.archive_file.load_lambda.output_base64sha256
}