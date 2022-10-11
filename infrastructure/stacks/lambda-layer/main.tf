resource "aws_lambda_layer_version" "lambda_layer" {
  filename            = "python.zip"
  layer_name          = var.uec_dos_tasks_python_libs
  compatible_runtimes = ["python3.8"]
}
