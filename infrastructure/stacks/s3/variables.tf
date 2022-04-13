# ############################
# # S3
# ############################

variable "texas_s3_logs_bucket" {
  description = "Texas logs bucket"
}

variable "environment_list" {
  description = "List of environments"
  type        = list(string)
}
