resource "aws_lambda_layer_version" "lambda_layer" {
  filename            = "python.zip"
  layer_name          = "uec-dos-tasks-python-libs"
  compatible_runtimes = ["python3.8"]
}
