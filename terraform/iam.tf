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
  name   = "tf-example-policy"
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
