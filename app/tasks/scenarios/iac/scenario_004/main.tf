provider "aws" {
  region = var.region
}

resource "aws_vpc" "data_pipeline" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "data-pipeline-vpc"
    Environment = "production"
  }
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.data_pipeline.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region}a"

  tags = {
    Name = "data-pipeline-private-a"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.data_pipeline.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region}b"

  tags = {
    Name = "data-pipeline-private-b"
  }
}

resource "aws_glue_catalog_database" "analytics" {
  name = "analytics_db"
}

resource "aws_glue_crawler" "data_crawler" {
  database_name = aws_glue_catalog_database.analytics.name
  name          = "data-pipeline-crawler"
  role          = aws_iam_role.glue_service.arn

  s3_target {
    path = "s3://${aws_s3_bucket.raw_data.bucket}/raw/"
  }
}
