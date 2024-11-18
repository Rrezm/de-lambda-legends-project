variable "credentials" {
  description = "Database credentials"
  type        = map(any)
  sensitive   = true
}
