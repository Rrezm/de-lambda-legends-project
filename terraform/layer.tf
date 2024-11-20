resource "null_resource" "create_dependencies" {
  provisioner "local-exec" {
    command = "pip install -r ${path.module}/../requirements.txt -t ${path.module}/../dependencies/python"
  }

  triggers = {
    dependencies = filemd5("${path.module}/../requirements.txt")
  }
}



data "archive_file" "layer" {

  type             = "zip"
  output_file_mode = "0666"
  source_dir      = "${path.module}/../dependencies"
  output_path      = "${path.module}/../layer/layer.zip"
  depends_on = [null_resource.create_dependencies]
}


resource "aws_lambda_layer_version" "lambda_layer" {
  layer_name          = "lambda_layer"

  s3_bucket           = aws_s3_bucket.lambda_code_bucket.bucket
  s3_key              = aws_s3_object.layer_code.key
}


resource "null_resource" "create_dependencies2" {
  provisioner "local-exec" {
    command = "pip install -r ${path.module}/../requirements2.txt -t ${path.module}/../dependencies2/python"
  }

  triggers = {
    dependencies = filemd5("${path.module}/../requirements2.txt")
  }
}



data "archive_file" "layer2" {

  type             = "zip"
  output_file_mode = "0666"
  source_dir      = "${path.module}/../dependencies2"
  output_path      = "${path.module}/../layer/layer2.zip"
  depends_on = [null_resource.create_dependencies2]
}


resource "aws_lambda_layer_version" "lambda_layer2" {
  layer_name          = "lambda_layer2"

  s3_bucket           = aws_s3_bucket.lambda_code_bucket.bucket
  s3_key              = aws_s3_object.layer_code.key
}

