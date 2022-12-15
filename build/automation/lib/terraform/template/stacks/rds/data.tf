# ==============================================================================
# Data
data "aws_vpcs" "vpcs" {
  tags = {
    Name = var.vpc_name
  }
}

data "aws_vpc" "vpc" {
  count = length(data.aws_vpcs.vpcs.ids)
  id    = tolist(data.aws_vpcs.vpcs.ids)[count.index]
}

data "aws_subnet_ids" "texas_private_subnet_ids" {
  vpc_id = data.aws_vpc.vpc[0].id
  tags = {
    Name = "lk8s-${var.aws_account_name}.texasplatform.uk-private-*"
  }
}

data "aws_subnet" "texas_subnet" {
  count = length(data.aws_subnet_ids.texas_subnet_ids.ids)
  id    = tolist(data.aws_subnet_ids.texas_subnet_ids.ids)[count.index]
}

data "aws_security_group" "default_vpc_sg" {
  name = "default"
}

#  Used by build/automation/lib/terraform/template/stacks/rds/main.tf
#  replaced by the above data sources
# data "terraform_remote_state" "networking" {
#   backend = "s3"
#   config = {
#     key    = "${var.terraform_state_key_shared}/networking/terraform.state"
#     bucket = var.terraform_state_store
#     region = var.aws_region
#   }
# }

#  Not used ?
# data "terraform_remote_state" "terraform-state" {
#   backend = "s3"
#   config = {
#     key    = "${var.terraform_state_key_shared}/terraform-state/terraform.state"
#     bucket = var.terraform_state_store
#     region = var.aws_region
#   }
# }

# ==============================================================================
# Terraform state keys and store set by the Make DevOps automation scripts

# variable "terraform_state_store" {}
# variable "terraform_state_key_shared" {}
