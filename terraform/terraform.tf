variable "aws_region" {
  type        = string
  description = "AWS region where resources will be provided"
}
variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket to be created"

}


terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
  required_version = ">= 1.14.3"
}

provider "aws" {
  region = var.aws_region

}

resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "s3_bucket_versioning" {
  bucket = aws_s3_bucket.s3_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}




data "aws_iam_policy_document" "iam_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:PutObject"
    ]
    resources = ["${aws_s3_bucket.s3_bucket.arn}/*"]
  }
}

resource "aws_iam_user" "iam_user" {
  name = "Test-User"
}

resource "aws_iam_policy" "policy_document" {
  name   = "tf-examplet-policy"
  policy = data.aws_iam_policy_document.iam_policy.json
}


resource "aws_iam_policy_attachment" "attach" {
  name       = aws_iam_user.iam_user.name
  users      = ["${aws_iam_user.iam_user.name}"]
  policy_arn = aws_iam_policy.policy_document.arn
}

resource "aws_iam_access_key" "access_key" {
  user = aws_iam_user.iam_user.name
}

output "id" {
  value     = aws_iam_access_key.access_key.id
  sensitive = true
}
output "secret" {
  value     = aws_iam_access_key.access_key.secret
  sensitive = true
}
