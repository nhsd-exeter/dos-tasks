resource "aws_lambda_function" "lambda" {
  function_name = "${var.service_prefix}-${var.name}-lambda"
  role          = aws_iam_role.lambda_role.arn
  publish       = true
  package_type  = "Image"
  image_uri     = var.image_uri

  timeout     = var.timeout
  memory_size = var.memory_size

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.tags
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = var.env_vars
  }
  depends_on = [
    aws_iam_role.lambda_role,
    aws_iam_role_policy.lambda_role_policy,
    aws_cloudwatch_log_group.lambda_log_group
  ]
}

resource "aws_lambda_function_event_invoke_config" "lambda_invoke_config" {
  function_name          = aws_lambda_function.lambda.function_name
  maximum_retry_attempts = var.retry_attempts
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.service_prefix}-${var.name}-role"
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

resource "aws_iam_role_policy" "lambda_role_policy" {
  name   = "${var.service_prefix}-${var.name}-role-policy"
  role   = aws_iam_role.lambda_role.name
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
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
        "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:uec-dos*",
        "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:core-dos*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": [
        "${var.s3_bucket_arn}",
        "${var.s3_bucket_arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface",
        "ec2:AssignPrivateIpAddresses",
        "ec2:UnassignPrivateIpAddresses",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeSubnets",
        "ec2:DescribeVpcs"
      ],
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "rds-db:connect"
      ],
      "Resource": [
        "arn:aws:rds:${var.aws_region}:${var.aws_account_id}:db:dos-*",
        "arn:aws:rds:${var.aws_region}:${var.aws_account_id}:db:core-dos-*",
        "arn:aws:rds:${var.aws_region}:${var.aws_account_id}:db:uec-dos-*",
        "arn:aws:rds:${var.aws_region}:${var.aws_account_id}:db:uec-core-dos-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction",
        "lambda:InvokeAsync"
      ],
      "Resource": [
        "arn:aws:lambda:${var.aws_region}:${var.aws_account_id}:function:${var.service_prefix}-*",
        "arn:aws:lambda:${var.aws_region}:${var.aws_account_id}:function:${var.service_prefix}-*:*"
      ]
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

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.service_prefix}-${var.name}-lambda"
  retention_in_days = var.log_retention
}

resource "aws_cloudwatch_log_subscription_filter" "splunk_firehose_subscription" {
  name            = "${var.service_prefix}-${var.name}-log-subscription"
  role_arn        = "arn:aws:iam::${var.aws_account_id}:role/${var.splunk_firehose_role}"
  filter_pattern  = ""
  log_group_name  = aws_cloudwatch_log_group.lambda_log_group.name
  destination_arn = "arn:aws:firehose:${var.aws_region}:${var.aws_account_id}:deliverystream/${var.splunk_firehose_subscription}"
}
