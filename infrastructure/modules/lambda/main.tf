resource "aws_lambda_function" "lambda" {
  function_name = "${var.service_prefix}-${var.name}-lambda"
  role          = aws_iam_role.lambda_role.arn
  publish       = true
  package_type  = "Image"
  image_uri     = "${var.aws_lambda_ecr}/${var.project_group_short}/${var.project_name_short}/${var.name}:${var.image_version}"

  timeout     = var.timeout
  memory_size = var.memory_size

  vpc_config {
    subnet_ids         = [data.terraform_remote_state.vpc.outputs.private_subnets[0], data.terraform_remote_state.vpc.outputs.private_subnets[1], data.terraform_remote_state.vpc.outputs.private_subnets[2]]
    security_group_ids = [data.terraform_remote_state.security_groups.outputs.lambda_security_group_id]
  }

  tags = var.tags
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = var.environment
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
      "Resource": [
        "${data.terraform_remote_state.s3.outputs.s3_bucket_id}",
        "${data.terraform_remote_state.s3.outputs.s3_bucket_id}/*"
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
        "rds-db:connect",
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
