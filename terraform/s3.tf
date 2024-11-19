resource "aws_s3_bucket" "ingested_bucket"{
    bucket = "ingested-data-lambda-legends-24"
      force_destroy = true 
tags = {
  Name = "ingested-data-lambda-legends-24"
  Environmnent = "Dev"
  Project = "Lambda Legends Data Processor"

}
}

resource "aws_s3_bucket" "lambda_code_bucket" {

  bucket_prefix = "lambda-extract-code-bucket-"
  force_destroy = true 

tags = {
  Name = "lambda-extract-code-bucket-"
  Environmnent = "Dev"
  Project = "Lambda Legends Data Processor"

}
}


resource "aws_s3_object" "lambda_code" {
bucket =  aws_s3_bucket.lambda_code_bucket.bucket
key    =  "ingestion_lambda/extract_data.zip"
source      = data.archive_file.lambda.output_path
source_hash = data.archive_file.lambda.output_base64sha256
}

resource "aws_s3_object" "layer_code" {
bucket =  aws_s3_bucket.lambda_code_bucket.bucket
key    =  "layer/layer.zip"
source =  data.archive_file.layer.output_path
depends_on = [ data.archive_file.layer]
}

resource "aws_s3_bucket" "processed_bucket"{
  bucket = "processed-data-lambda-legends-24"
  force_destroy = true 
  tags = {
    Name = "processed-data-lambda-legends-24"
    Environmnent = "Dev"
    Project = "Lambda Legends Data Processor"
  }
}

resource "aws_s3_bucket" "processed_lambda_code_bucket" {

  bucket = "processed-code-lambda-legends-24"
  force_destroy = true 

  tags = {
    Name = "processed-code-lambda-legends-24"
    Environmnent = "Dev"
    Project = "Lambda Legends Data Processor"
  }
}

resource "aws_s3_object" "transform_lambda_code" {
bucket =  aws_s3_bucket.processed_lambda_code_bucket.bucket
key    =  "processed_lambda_code_bucket/transform_lambda.zip"
source      = data.archive_file.lambda.output_path
source_hash = data.archive_file.lambda.output_base64sha256
}