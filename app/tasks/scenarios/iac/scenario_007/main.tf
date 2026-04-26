provider "aws" { region = "us-east-1" }

resource "aws_db_instance" "analytics" {
  identifier              = "analytics-prod"
  engine                  = "postgres"
  engine_version          = "13.7"
  instance_class          = "db.t3.medium"
  allocated_storage       = 100
  username                = "admin"
  password                = "changeme123"
  publicly_accessible     = true
  storage_encrypted       = false
  backup_retention_period = 0
  skip_final_snapshot     = true
}

resource "aws_security_group" "db_sg" {
  name        = "db-sg"
  description = "DB security group"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ebs_volume" "data" {
  availability_zone = "us-east-1a"
  size              = 200
  encrypted         = false
  type              = "gp3"
}
