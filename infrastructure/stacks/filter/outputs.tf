output "filter_lambda_arn" {
  description = "ARN value for the HK Filter Lambda function"
  value       = module.filter_lambda.lambda_arn
}

output "filter_lambda_qualified_arn" {
  value = module.filter_lambda.lambda_qualified_arn
}

output "filter_lambda_version" {
  value = module.filter_lambda.lambda_version
}
