resource "aws_iam_policy" "app_policy" {
  name = "app-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_s3_bucket" "uploads" {
  bucket = "company-uploads-prod"
}

resource "aws_s3_bucket_acl" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  acl    = "public-read-write"
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_cloudtrail" "audit" {
  name                          = "audit-trail"
  s3_bucket_name                = aws_s3_bucket.uploads.id
  enable_log_file_validation    = false
  is_multi_region_trail         = false
}
