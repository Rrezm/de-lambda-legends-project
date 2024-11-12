
resource "null_resource" "create_dependencies" {
  provisioner "local-exec" {
    command = "pip install -r ${path.module}/../requirements.txt -t ${path.module}/../dependencies/python"
  }

  triggers = {
    dependencies = filemd5("${path.module}/../requirements.txt")
  }
}
## Team 1 is currently working on this
## Lambda python code, has to be zipped before uploading to aws



data "archive_file" "layer" {

  type             = "zip"
  output_file_mode = "0666"
  source_file      = "${path.module}/dependencies"
  output_path      = "${path.module}/../layer/layer.zip"
}

 ## Layer is necessary as it zips ibraries, modules, or packages that your Lambda function requires to run but that aren’t included in AWS Lambda by default.

resource "aws_lambda_layer_version" "lambda_layer" {
  layer_name          = "lambda_layer"
  compatible_runtimes = "python 3.11"
  s3_bucket           = aws_s3_bucket.ingested_bucket.bucket
  s3_key              = "layers/layer.zip"
}