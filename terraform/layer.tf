
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
