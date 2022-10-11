data "terraform_remote_state" "s3" {
  backend = "s3"
  config = {
    bucket = var.texas_terraform_state_store
    key    = var.s3_tf_state_key
    region = var.aws_region
  }
}

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.vpc_terraform_state_key
    region = var.aws_region
  }
}

data "terraform_remote_state" "security_groups" {
  backend = "s3"
  config = {
    bucket = var.texas_terraform_state_store
    key    = var.security_groups_tf_state_key
    region = var.aws_region
  }
}

data "aws_lambda_layer_version" "uec_dos_tasks_python_libs" {
  layer_name = var.uec_dos_tasks_python_libs
}