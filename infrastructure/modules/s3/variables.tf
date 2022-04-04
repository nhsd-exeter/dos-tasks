
# ==============================================================================
# Mandatory variables

variable "bucket_name" { description = "The S3 bucket name" }
variable "bucket_iam_role" { description = "The Bucket IAM Role" }
variable "log_bucket" { description = "Name of the S3 log bucket" }
variable "service_name" { description = "Name of the service" }

# ==============================================================================
# Default variables

variable "attach_policy" { default = false }

# ==============================================================================
# Context

variable "tags" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
