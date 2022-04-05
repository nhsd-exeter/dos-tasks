data "terraform_remote_state" "s3" {
  backend = "s3"
  config = {
    bucket = var.texas_terraform_state_store
    key    = var.s3_tf_state_key
    region = var.aws_region
  }
}
