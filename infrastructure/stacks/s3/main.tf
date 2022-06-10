module "housekeeping_bucket" {
  source          = "../../modules/s3"
  bucket_name     = "${var.service_prefix}-housekeeping-bucket"
  bucket_iam_role = "${var.service_prefix}-housekeeping-bucket-role"
  attach_policy   = true
  log_bucket      = var.texas_s3_logs_bucket
  service_name    = var.project_group_short
  tags            = local.standard_tags
}

resource "aws_s3_bucket_object" "folders" {
  count = length(var.environment_list)

  bucket = module.housekeeping_bucket.s3_bucket_id
  acl    = "private"
  key    = "${var.environment_list[count.index]}/archive/"
  source = "/dev/null"
}
