resource "aws_vpc" "management" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "management-vpc"
    Environment = "management"
  }
}

resource "aws_subnet" "management_public" {
  vpc_id                  = aws_vpc.management.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "management-public-subnet"
  }
}

resource "aws_subnet" "management_private" {
  vpc_id            = aws_vpc.management.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region}b"

  tags = {
    Name = "management-private-subnet"
  }
}

resource "aws_internet_gateway" "management" {
  vpc_id = aws_vpc.management.id

  tags = {
    Name = "management-igw"
  }
}

resource "aws_route_table" "management_public" {
  vpc_id = aws_vpc.management.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.management.id
  }

  tags = {
    Name = "management-public-rt"
  }
}
