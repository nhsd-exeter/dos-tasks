output "referralroles_lambda_arn" {
  description = "ARN value for the HK ReferralRoles Lambda function"
  value       = module.referralroles_lambda.lambda_arn
}

output "referralroles_lambda_qualified_arn" {
  value = module.referralroles_lambda.lambda_qualified_arn
}

output "referralroles_lambda_version" {
  value = module.referralroles_lambda.lambda_version
}
