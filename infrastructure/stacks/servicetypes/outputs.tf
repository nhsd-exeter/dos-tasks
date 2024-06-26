output "servicetypes_lambda_arn" {
  description = "ARN value for the HK Service Types Lambda function"
  value       = module.servicetypes_lambda.lambda_arn
}

output "servicetypes_lambda_qualified_arn" {
  value = module.servicetypes_lambda.lambda_qualified_arn
}

output "servicetypes_lambda_version" {
  value = module.servicetypes_lambda.lambda_version
}
