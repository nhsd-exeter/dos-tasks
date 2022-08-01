output "integrationtest_lambda_arn" {
  description = "ARN value for the HK integration test Lambda function"
  value       = module.integrationtest_lambda.lambda_arn
}

output "integrationtest_lambda_qualified_arn" {
  value = module.integrationtest_lambda.lambda_qualified_arn
}

output "integrationtest_lambda_version" {
  value = module.integrationtest_lambda.lambda_version
}
