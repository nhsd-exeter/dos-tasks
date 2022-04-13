module "s3" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "3.0.1"
  tags    = var.tags

  bucket        = var.bucket_name
  attach_policy = var.attach_policy
  policy        = data.aws_iam_policy_document.bucket_policy.json

  force_destroy           = false
  acl                     = "private"
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
  versioning = {
    enabled = true
  }
  logging = {
    target_bucket = var.log_bucket
    target_prefix = "logs/${var.service_name}/${var.bucket_name}/"
  }
}


resource "aws_iam_role" "this" {

  name = var.bucket_iam_role
  path = "/"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": { "Service": "s3.amazonaws.com" },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "bucket_policy" {
  statement {
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.this.arn]
    }
    sid    = "IAMS3BucketPermissions"
    effect = "Allow"

    resources = ["arn:aws:s3:::${var.bucket_name}"]


    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:ListBucketVersions",
    ]
  }

  statement {
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.this.arn]
    }
    sid    = "IAMS3ObjectPermissions"
    effect = "Allow"

    resources = ["arn:aws:s3:::${var.bucket_name}/*"]

    actions = [
      "s3:AbortMultipartUpload",
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:ListMultipartUploadParts",
      "s3:PutObject",
    ]
  }

  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    effect  = "Deny"
    actions = ["*"]
    resources = [
      "arn:aws:s3:::${var.bucket_name}",
      "arn:aws:s3:::${var.bucket_name}/*",
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}
