# Context

locals {

  context = {

    aws_account_id   = var.aws_account_id
    aws_account_name = var.aws_account_name
    aws_region       = var.aws_region
    aws_profile      = var.aws_profile

    programme           = var.programme
    project_group       = var.project_group
    project_group_short = var.project_group_short
    project_name        = var.project_name
    project_name_short  = var.project_name_short
    service_tag         = var.service_tag
    project_tag         = var.project_tag
    profile             = var.profile
    service_prefix      = var.service_prefix
    environment         = var.environment
  }

  standard_tags = {
    Programme   = var.programme
    Service     = "core-dos"
    Project     = "core-dos"
    Environment = var.profile
  }
}
