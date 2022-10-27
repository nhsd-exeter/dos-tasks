data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.vpc_terraform_state_key
    region = var.aws_region
  }
}

# Look up for rds instance
data "aws_db_instance" "rds_instance" {
  db_instance_identifier = var.db_identifier
}
