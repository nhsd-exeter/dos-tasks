resource "aws_iam_role" "lambda_iam_role" {
  name               = var.migration_lambda_iam_name
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "DoSServiceDeveloperSecretManagerAccess" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = data.aws_iam_policy.iam_policy.arn
}
