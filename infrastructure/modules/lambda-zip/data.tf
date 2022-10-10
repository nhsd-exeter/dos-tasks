# Lambda
data "archive_file" "integration_test_lambda_function_archive" {
  type        = "zip"
  source_dir  = "${path.module}/../../stacks/integration-zip/function/"
  output_path = "${path.module}/functions_zip/${var.service_prefix}-${var.name}-lambda.zip"
}
