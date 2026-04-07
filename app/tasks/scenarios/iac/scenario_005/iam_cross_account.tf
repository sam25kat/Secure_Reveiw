resource "aws_iam_role" "cross_account_admin" {
  name = "cross-account-admin-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Action    = "sts:AssumeRole"
        Principal = {
          AWS = "*"
        }
      }
    ]
  })

  tags = {
    Name        = "cross-account-admin"
    Environment = "management"
  }
}

resource "aws_iam_role_policy_attachment" "cross_account_admin" {
  role       = aws_iam_role.cross_account_admin.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_role" "dev_account_deploy" {
  name = "dev-account-deploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Action    = "sts:AssumeRole"
        Principal = {
          AWS = "arn:aws:iam::${var.dev_account_id}:root"
        }
      }
    ]
  })

  tags = {
    Name        = "dev-deploy-role"
    Environment = "management"
  }
}

resource "aws_iam_role_policy" "dev_deploy_policy" {
  name = "dev-deploy-policy"
  role = aws_iam_role.dev_account_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "s3:*",
          "rds:*",
          "lambda:*"
        ]
        Resource = "*"
      }
    ]
  })
}
