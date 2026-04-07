provider "aws" {
  region = var.region
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "app-vpc"
    Environment = "production"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "app-public-subnet"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region}b"

  tags = {
    Name = "app-private-subnet"
  }
}

resource "aws_s3_bucket" "app_data" {
  bucket = "app-data-prod-${var.region}"

  tags = {
    Name        = "app-data-prod"
    Environment = "production"
  }
}

resource "aws_s3_bucket_policy" "app_data_policy" {
  bucket = aws_s3_bucket.app_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadAccess"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.app_data.arn}/*"
      }
    ]
  })
}

resource "aws_security_group" "web_sg" {
  name        = "web-server-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-server-sg"
  }
}

resource "aws_instance" "web" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}

resource "aws_db_subnet_group" "app_db" {
  name       = "app-db-subnet-group"
  subnet_ids = [aws_subnet.public.id, aws_subnet.private.id]

  tags = {
    Name = "app-db-subnet-group"
  }
}

resource "aws_db_instance" "app_db" {
  identifier           = "app-db"
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.medium"
  allocated_storage    = 50
  db_name              = "appdb"
  username             = "admin"
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.app_db.name
  skip_final_snapshot  = true
  storage_encrypted    = false

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = {
    Name        = "app-db"
    Environment = "production"
  }
}
