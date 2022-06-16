output "symptomgroups_lambda_arn" {
  description = "ARN value for the HK symptomgroups Lambda function"
  value       = module.symptomgroups_lambda.lambda_arn
}

output "symptomgroups_lambda_qualified_arn" {
  value = module.symptomgroups_lambda.lambda_qualified_arn
}

output "symptomgroups_lambda_version" {
  value = module.symptomgroups_lambda.lambda_version
}
