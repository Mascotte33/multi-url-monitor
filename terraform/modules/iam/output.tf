output "access_id_key" {
  value     = aws_iam_access_key.access_key.id
  sensitive = true
}

output "access_secret_key" {
  value     = aws_iam_access_key.access_key.secret
  sensitive = true
}
