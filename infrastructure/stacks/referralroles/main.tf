resource "aws_lambda_function" "hk_referralroles_lambda" {
  function_name = "${var.service_prefix}-hk-referralroles-lambda"
  role          = aws_iam_role.hk_referralroles_lambda_role.arn
  publish       = true
  package_type  = "Image"
  timeout       = "30"
  image_uri     = "${var.aws_lambda_ecr}/${var.project_group_short}/${var.project_name_short}/hk-referralroles:${var.image_version}"
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = {
      "" = ""
    }
  }
  depends_on = [
    aws_iam_role.hk_referralroles_lambda_role,
    aws_iam_role_policy.hk_referralroles_lambda_role_policy,
    aws_cloudwatch_log_group.hk_referralroles_lambda_log_group
  ]
}

resource "aws_lambda_function_event_invoke_config" "hk_referralroles_lambda_invoke_config" {
  function_name          = aws_lambda_function.hk_referralroles_lambda.function_name
  maximum_retry_attempts = 0
}

resource "aws_iam_role" "hk_referralroles_lambda_role" {
  name               = "${var.service_prefix}-hk-referralroles-role"
  path               = "/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "hk_referralroles_lambda_role_policy" {
  name   = "${var.service_prefix}-hk-referralroles-role-policy"
  role   = aws_iam_role.hk_referralroles_lambda_role.name
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:Describe*",
        "secretsmanager:Get*",
        "secretsmanager:List*"
      ],
      "Resource": [
        "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:${var.project_group_short}*",
        "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:core-dos*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": "${data.terraform_remote_state.s3.outputs.s3_bucket_id}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "xray:PutTraceSegments",
        "xray:PutTelemetryRecords",
        "xray:GetSamplingRules",
        "xray:GetSamplingTargets",
        "xray:GetSamplingStatisticSummaries"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}
POLICY
}

resource "aws_cloudwatch_log_group" "hk_referralroles_lambda_log_group" {
  name              = "/aws/lambda/${var.service_prefix}-hk-referralroles-lambda"
  retention_in_days = "0"
}
