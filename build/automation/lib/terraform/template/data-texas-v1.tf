# ==============================================================================
# Data

# Not used but replace with data aws_eks_cluster ?
# data "terraform_remote_state" "eks" {
#   backend = "s3"
#   config = {
#     key    = var.eks_terraform_state_key
#     bucket = var.terraform_platform_state_store
#     region = var.aws_region
#   }
# }

# data "aws_eks_cluster" "cluster" {
#   name = "example"
# }


# Not used ? Replace with daga.aws_route53_zone ?
# data "terraform_remote_state" "route53" {
#   backend = "s3"
#   config = {
#     key    = var.route53_terraform_state_key
#     bucket = var.terraform_platform_state_store
#     region = var.aws_region
#   }
# }

# data "aws_route53_zone" "selected" {
#   name         = "test.com."
#   private_zone = true
# }

#  Not used ?
# data "terraform_remote_state" "security_groups_k8s" {
#   backend = "s3"
#   config = {
#     key    = var.security_groups_k8s_terraform_state_key
#     bucket = var.terraform_platform_state_store
#     region = var.aws_region
#   }
# }

#  Not used ?
# data "terraform_remote_state" "security_groups" {
#   backend = "s3"
#   config = {
#     key    = var.security_groups_terraform_state_key
#     bucket = var.terraform_platform_state_store
#     region = var.aws_region
#   }
# }

# Not Used but replaced with aws_vpc below
# data "terraform_remote_state" "vpc" {
#   backend = "s3"
#   config = {
#     key    = var.vpc_terraform_state_key
#     bucket = var.terraform_platform_state_store
#     region = var.aws_region
#   }
# }

#
# variable "vpc_name" {}
#
# ==============================================================================
# Terraform state keys and store set by the Make DevOps automation scripts

# variable "terraform_platform_state_store" {}

# variable "eks_terraform_state_key" {}
# variable "route53_terraform_state_key" {}
# variable "security_groups_k8s_terraform_state_key" {}
# variable "security_groups_terraform_state_key" {}
# variable "vpc_terraform_state_key" {}
