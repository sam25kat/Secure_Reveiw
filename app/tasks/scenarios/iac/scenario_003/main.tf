provider "aws" {
  region = var.region
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_eks_cluster" "main" {
  name     = "production-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = aws_subnet.public[*].id
    endpoint_public_access  = true
    endpoint_private_access = false
    security_group_ids      = [aws_security_group.eks_cluster.id]
  }

  tags = {
    Name        = "production-cluster"
    Environment = "production"
  }
}

resource "aws_eks_node_group" "workers" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "production-workers"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = aws_subnet.public[*].id

  scaling_config {
    desired_size = 3
    max_size     = 5
    min_size     = 2
  }

  instance_types = ["t3.large"]

  launch_template {
    id      = aws_launch_template.eks_nodes.id
    version = "$Latest"
  }

  tags = {
    Name        = "production-workers"
    Environment = "production"
  }
}

resource "aws_launch_template" "eks_nodes" {
  name_prefix   = "eks-node-"
  instance_type = "t3.large"

  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_size = 50
      volume_type = "gp3"
      encrypted   = false
    }
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "eks-worker-node"
    }
  }
}
