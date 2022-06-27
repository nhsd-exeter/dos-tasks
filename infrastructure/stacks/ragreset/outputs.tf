output "lambda_arn" {
  description = "ARN value for the scheduled ragreset Lambda function"
  value       = module.ragreset_lambda.lambda_arn
}

output "lambda_qualified_arn" {
  description = "Fully qualified arn of lambda"
  value       = module.ragreset_lambda.lambda_qualified_arn
}

output "lambda_version" {
  description = "Version of lambda function"
  value       = module.ragreset_lambda.lambda_version
}

