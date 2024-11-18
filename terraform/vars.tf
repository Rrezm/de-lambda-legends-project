# variable "credentials" {
#   description = "Database credentials"
#   type        = map(any)
#   sensitive   = true
# }

variable "credentials" {
  default = {
    cohort_id = "de_2024_09_02"
    user = "project_team_7"
    password = "ArveGgGcbzTaEOT"
    host = "nc-data-eng-totesys-production.chpsczt8h1nu.eu-west-2.rds.amazonaws.com"
    database = "totesys"
    port = 5432
  }
  sensitive = true
  type = map(any)
}