module "filter_lambda" {
  source = "../../modules/lambda"
  name   = "hk-filter"
}

resource "aws_lambda_permission" "hk_bucket_trigger" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = module.filter_lambda.lambda_arn
  principal     = "s3.amazonaws.com"
  source_arn    = data.terraform_remote_state.s3.outputs.s3_bucket_arn
}

resource "aws_s3_bucket_notification" "hk_bucket_notification" {
  bucket = data.terraform_remote_state.s3.outputs.s3_bucket_id

  lambda_function {
    lambda_function_arn = module.filter_lambda.lambda_arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.hk_bucket_trigger]
}
