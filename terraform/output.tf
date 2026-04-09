output "id" {
  value     = aws_iam_access_key.access_key.id
  sensitive = true
}
output "secret" {
  value     = aws_iam_access_key.access_key.secret
  sensitive = true
}
