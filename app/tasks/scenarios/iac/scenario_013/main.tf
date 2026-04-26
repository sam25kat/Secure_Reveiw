resource "aws_eks_cluster" "main" {
  name     = "production-cluster"
  role_arn = aws_iam_role.eks.arn
  version  = "1.21"

  vpc_config {
    subnet_ids              = aws_subnet.private[*].id
    endpoint_private_access = false
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  encryption_config {
    resources = []
  }
}

resource "aws_eks_node_group" "workers" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "workers"
  node_role_arn   = aws_iam_role.nodes.arn
  subnet_ids      = aws_subnet.private[*].id

  scaling_config {
    desired_size = 3
    min_size     = 3
    max_size     = 10
  }

  remote_access {
    ec2_ssh_key                = "prod-key"
    source_security_group_ids = []
  }

  ami_type = "AL2_x86_64"
}
