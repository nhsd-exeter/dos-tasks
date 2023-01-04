module "hk_iam_role" {
  source         = "../../modules/iam_role"
  name           = var.housekeeping_role_name
  s3_bucket_arn  = data.aws_s3_bucket.housekeeping_bucket.arn
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  service_prefix = var.service_prefix
  tags           = local.standard_tags
}
