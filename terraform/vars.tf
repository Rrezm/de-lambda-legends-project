variable "credentials" {
  description = "Database credentials"
  type        = map(any)
  sensitive   = true
}

variable "dw_credentials" {
  description = "Datawarehouse credentials"
  type        = map(any)
  sensitive   = true
}
