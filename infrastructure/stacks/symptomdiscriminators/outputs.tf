output "referralroles_lambda_arn" {
  description = "ARN value for the HK Symptom Discriminators Lambda function"
  value       = module.symptomdiscriminators_lambda.lambda_arn
}

output "symptomdiscriminators_lambda_qualified_arn" {
  value = module.symptomdiscriminators_lambda.lambda_qualified_arn
}

output "symptomdiscriminators_lambda_version" {
  value = module.symptomdiscriminators_lambda.lambda_version
}
