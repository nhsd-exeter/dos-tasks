output "integration_test_lambda_arn" {
  description = "ARN value for the HK integration test Lambda function"
  value       = module.integration_test_lambda.lambda_arn
}

output "integration_test_lambda_qualified_arn" {
  value = module.integration_test_lambda.lambda_qualified_arn
}

output "integration_test_lambda_version" {
  value = module.integration_test_lambda.lambda_version
}
