output "stt_lambda_arn" {
  description = "ARN value for the HK stt scenario upload Lambda function"
  value       = module.stt_lambda.lambda_arn
}

output "stt_lambda_qualified_arn" {
  value = module.stt_lambda.lambda_qualified_arn
}

output "stt_lambda_version" {
  value = module.stt_lambda.lambda_version
}
