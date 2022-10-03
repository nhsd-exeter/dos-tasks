output "symptomgroupdiscriminators_lambda_arn" {
  description = "ARN value for the HK Symptom Group Symptom Discriminators Lambda function"
  value       = module.symptomgroupdiscriminators_lambda.lambda_arn
}

output "symptomgroupdiscriminators_lambda_qualified_arn" {
  value = module.symptomgroupdiscriminators_lambda.lambda_qualified_arn
}

output "symptomgroupdiscriminators_lambda_version" {
  value = module.symptomgroupdiscriminators_lambda.lambda_version
}
