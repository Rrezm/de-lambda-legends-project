resource "aws_secretsmanager_secret" "db_credentials" {
  name = "db_credentials22"
  recovery_window_in_days = 0
}

 resource "aws_secretsmanager_secret_version" "db_credentials" {
    secret_id = aws_secretsmanager_secret.db_credentials.id
    secret_string = jsonencode(var.credentials)
 }
 
 resource "aws_secretsmanager_secret" "dw_credentials" {
  name = "db_credentials23"
  recovery_window_in_days = 0
}

 resource "aws_secretsmanager_secret_version" "dw_credentials" {
    secret_id = aws_secretsmanager_secret.dw_credentials.id
    secret_string = jsonencode(var.dw_credentials)
 }