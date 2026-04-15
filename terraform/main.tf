terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
  backend "s3" {
    bucket       = "multi-url-monitor-terraform-infra"
    key          = "url-monitoring/prod/terraform.tfstate"
    region       = "eu-central-1"
    use_lockfile = true
  }
  required_version = ">= 1.14.3"
}

provider "aws" {
  region = var.aws_region

}

module "s3" {
  source      = "./modules/s3"
  bucket_name = var.bucket_name
}

module "iam" {
  source     = "./modules/iam"
  bucket_arn = module.s3.bucket_arn
}
