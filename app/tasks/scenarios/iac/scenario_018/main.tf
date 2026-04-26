# CloudTrail + audit log bucket for compliance
# Reviewer: please flag any audit-trail integrity / coverage gaps

resource "aws_s3_bucket" "audit_logs" {
  bucket = "company-audit-logs"
  acl    = "public-read"
}

resource "aws_s3_bucket_versioning" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_cloudtrail" "main" {
  name                          = "main-trail"
  s3_bucket_name                = aws_s3_bucket.audit_logs.id
  is_multi_region_trail         = false
  include_global_service_events = false
  enable_log_file_validation    = false
  enable_logging                = true

  event_selector {
    read_write_type           = "WriteOnly"
    include_management_events = true
  }
}

resource "aws_lambda_function" "report_processor" {
  function_name = "report-processor"
  role          = "arn:aws:iam::123456789012:role/lambda-exec"
  handler       = "index.handler"
  runtime       = "python3.7"
  filename      = "report.zip"

  environment {
    variables = {
      DB_PASSWORD = "ProdDb!Pass2023"
      API_KEY     = "sk_test_EXAMPLE_FAKE_KEY_FOR_TESTING"
    }
  }
}
