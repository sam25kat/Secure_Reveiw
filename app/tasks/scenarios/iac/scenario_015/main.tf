# Production analytics database — provisioned via Terraform
# Owner: data-platform team
# Reviewer: please flag misconfigurations before this hits prod

provider "aws" {
  region = "us-east-1"
}

resource "aws_db_subnet_group" "analytics" {
  name       = "analytics-subnet-group"
  subnet_ids = ["subnet-0a1b2c3d", "subnet-4e5f6a7b"]
}

resource "aws_security_group" "analytics_db" {
  name        = "analytics-db-sg"
  description = "Allow inbound to analytics RDS"
  vpc_id      = "vpc-0123456789abcdef"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "analytics" {
  identifier             = "analytics-prod"
  engine                 = "postgres"
  engine_version         = "13.7"
  instance_class         = "db.r5.xlarge"
  allocated_storage      = 200
  username               = "admin"
  password               = "Sup3rSecret!2023"
  publicly_accessible    = true
  storage_encrypted      = false
  skip_final_snapshot    = true
  backup_retention_period = 0
  multi_az               = false
  vpc_security_group_ids = [aws_security_group.analytics_db.id]
  db_subnet_group_name   = aws_db_subnet_group.analytics.name

  tags = {
    Environment = "production"
    Team        = "data-platform"
  }
}

resource "aws_s3_bucket" "analytics_exports" {
  bucket = "analytics-exports-prod"
  acl    = "public-read"
}
