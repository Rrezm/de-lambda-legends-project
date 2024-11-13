resource "aws_secretsmanager_secret" "credentials" {
  name = "credentials"
}

 resource "aws_secretsmanager_secret_version" "credentials" {
    secret_id = aws_secretsmanager_secret.credentials.id
    secret_string = jsonencode(var.credentials)
 }
 