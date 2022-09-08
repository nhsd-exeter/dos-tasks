output "servicetypes_lambda_arn" {
  description = "ARN value for the HK Symptom Discriminators Lambda function"
  value       = module.sservicetypes_lambda.lambda_arn
}

output "servicetypes_lambda_qualified_arn" {
  value = module.servicetypes_lambda.lambda_qualified_arn
}

output "servicetypes_lambda_version" {
  value = module.servicetypes_lambda.lambda_version
}
