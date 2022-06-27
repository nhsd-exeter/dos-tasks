output "lambda_arn" {
  value = aws_lambda_function.lambda.arn
}

output "lambda_qualified_arn" {
  value = aws_lambda_function.lambda.qualified_arn
}

output "lambda_version" {
  value = aws_lambda_function.lambda.version
}

output "lambda_function_name" {
  value = aws_lambda_function.lambda.function_name
}
