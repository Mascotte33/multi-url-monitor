output "bucket_arn" {
  value     = aws_s3_bucket.s3_bucket.arn
  sensitive = true
}

output "bucket_id" {
  value     = aws_s3_bucket.s3_bucket.id
  sensitive = true
}
