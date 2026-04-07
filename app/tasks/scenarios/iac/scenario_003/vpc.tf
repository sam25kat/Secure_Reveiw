resource "aws_vpc" "eks" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name                                        = "eks-vpc"
    "kubernetes.io/cluster/production-cluster"   = "shared"
  }
}

resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.eks.id
  cidr_block        = cidrsubnet(aws_vpc.eks.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name                                        = "eks-public-${count.index}"
    "kubernetes.io/cluster/production-cluster"   = "shared"
    "kubernetes.io/role/elb"                     = "1"
  }
}

resource "aws_internet_gateway" "eks" {
  vpc_id = aws_vpc.eks.id

  tags = {
    Name = "eks-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.eks.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.eks.id
  }

  tags = {
    Name = "eks-public-rt"
  }
}

resource "aws_security_group" "eks_cluster" {
  name        = "eks-cluster-sg"
  description = "Security group for EKS cluster"
  vpc_id      = aws_vpc.eks.id

  ingress {
    description = "Allow all inbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "eks-cluster-sg"
  }
}
