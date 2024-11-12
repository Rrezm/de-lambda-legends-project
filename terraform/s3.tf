resource "aws_s3_bucket" "ingested_bucket"{
    bucket_prefix = "ingested-data-lambda-legends-24-"

tags = {
  Name = "ingested-data-lambda-legends-24-"
  Eviroment = "Dev"
  Project = "Lambda Legends Data Processor"

}
}

resource "aws_s3_bucket" "lambda_code_bucket" {

  Bucket_prefix = "lambda-extract-code-bucket-"
  force_destroy = true 

tags = {
  Name = "lambda-extract-code-bucket-"
  Eviroment = "Dev"
  Project = "Lambda Legends Data Processor"

}
}

resource "aws_s3_object" "lambda_code" {
bucket =  aws_s3_bucket.lambda_code_bucket.bucket
key    =  "extract_data_lambda_code.zip"
source =  "${path.module}/../extract_data.zip"
}

resource "aws_s3_object" "layer_code" {
bucket =  aws_s3_bucket.lambda_code_bucket.bucket
key    =  "layer_code.zip"
source =  "${path.module}/layer.zip"
}