variable "aws_region" {
  type        = string
  description = "AWS region where resources will be provided"
}
variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket to be created"

}
variable "alert_email" {
  type        = string
  description = "Email address for alerts"
}
