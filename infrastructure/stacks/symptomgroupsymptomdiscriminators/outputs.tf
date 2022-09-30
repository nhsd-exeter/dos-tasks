output "symptomgroupsymptomdiscriminators_lambda_arn" {
  description = "ARN value for the HK Symptom Group Symptom Discriminators Lambda function"
  value       = module.symptomgroupsymptomdiscriminators_lambda.lambda_arn
}

output "symptomgroupsymptomdiscriminators_lambda_qualified_arn" {
  value = module.symptomgroupsymptomdiscriminators_lambda.lambda_qualified_arn
}

output "symptomgroupsymptomdiscriminators_lambda_version" {
  value = module.symptomgroupsymptomdiscriminators_lambda.lambda_version
}
