resource "aws_secretsmanager_secret" "db_credentials" {
  name = "db_credentials16"
}

 resource "aws_secretsmanager_secret_version" "db_credentials" {
    secret_id = aws_secretsmanager_secret.db_credentials.id
    secret_string = jsonencode(var.credentials)
 }
 