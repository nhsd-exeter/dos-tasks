output "filter_lambda_arn" {
  description = "ARN value for the HK Filter Lambda function"
  value       = aws_lambda_function.hk_filter_lambda.arn
}
