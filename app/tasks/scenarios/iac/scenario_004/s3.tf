resource "aws_s3_bucket" "raw_data" {
  bucket = "data-pipeline-raw-${var.region}"

  tags = {
    Name        = "raw-data-bucket"
    Environment = "production"
  }
}

resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "raw_data_policy" {
  bucket = aws_s3_bucket.raw_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DataIngestionAccess"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject", "s3:PutObject"]
        Resource  = "${aws_s3_bucket.raw_data.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket" "processed_data" {
  bucket = "data-pipeline-processed-${var.region}"

  tags = {
    Name        = "processed-data-bucket"
    Environment = "production"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}
