output "lambda_security_group_id" {
  description = "ID of the Lambda security group"
  value       = aws_security_group.hk_lambda_sg.id
}
