output "symptomdiscriminatorsynonyms_lambda_arn" {
  description = "ARN value for the HK Symptom Discriminator Synonyms Lambda function"
  value       = module.symptomdiscriminatorsynonyms_lambda.lambda_arn
}

output "symptomdiscriminatorsynonyms_lambda_qualified_arn" {
  value = module.symptomdiscriminatorsynonyms_lambda.lambda_qualified_arn
}

output "symptomdiscriminatorsynonyms_lambda_version" {
  value = module.symptomdiscriminatorsynonyms_lambda.lambda_version
}
