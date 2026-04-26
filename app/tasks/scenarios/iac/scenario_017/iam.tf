# IAM policies + cross-account trust for the data-platform team
# Reviewer: please flag privilege boundary issues

resource "aws_iam_role" "data_platform" {
  name = "data-platform-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::999888777666:root"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "data_platform_full" {
  name = "data-platform-full-access"
  role = aws_iam_role.data_platform.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}

resource "aws_iam_user" "ci_deployer" {
  name = "ci-deployer"
}

resource "aws_iam_access_key" "ci_deployer" {
  user = aws_iam_user.ci_deployer.name
}

resource "aws_iam_user_policy" "ci_deployer_policy" {
  name = "ci-deployer-policy"
  user = aws_iam_user.ci_deployer.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:*",
        "iam:PassRole",
        "lambda:*"
      ]
      Resource = "*"
    }]
  })
}

output "ci_deployer_secret" {
  value = aws_iam_access_key.ci_deployer.secret
}
