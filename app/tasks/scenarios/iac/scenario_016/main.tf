# EKS cluster + node group for prod workloads
# Reviewer: please flag any control-plane / endpoint misconfigurations

provider "aws" {
  region = "us-west-2"
}

resource "aws_iam_role" "eks_cluster" {
  name = "eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_eks_cluster" "prod" {
  name     = "prod-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.21"

  vpc_config {
    subnet_ids              = ["subnet-0a1b2c3d", "subnet-4e5f6a7b"]
    endpoint_public_access  = true
    endpoint_private_access = false
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  enabled_cluster_log_types = []

  tags = {
    Environment = "production"
  }
}

resource "aws_eks_node_group" "prod_nodes" {
  cluster_name    = aws_eks_cluster.prod.name
  node_group_name = "prod-ng"
  node_role_arn   = aws_iam_role.eks_cluster.arn
  subnet_ids      = ["subnet-0a1b2c3d", "subnet-4e5f6a7b"]

  scaling_config {
    desired_size = 3
    max_size     = 5
    min_size     = 1
  }

  remote_access {
    ec2_ssh_key               = "prod-key"
    source_security_group_ids = []
  }

  instance_types = ["m5.large"]
}
