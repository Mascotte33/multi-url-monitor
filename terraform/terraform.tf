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


