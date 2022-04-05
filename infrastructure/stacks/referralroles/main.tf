module "referralroles_lambda" {
  source = "../../modules/lambda"
  name   = "hk-referralroles"
  tags   = local.standard_tags
}
