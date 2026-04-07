resource "aws_redshift_subnet_group" "data_pipeline" {
  name       = "data-pipeline-redshift-subnet"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "data-pipeline-redshift-subnet"
  }
}

resource "aws_redshift_cluster" "analytics" {
  cluster_identifier        = "analytics-warehouse"
  database_name             = "analytics"
  master_username           = "admin"
  master_password           = "Pr0duction#Pass2024!"
  node_type                 = "dc2.large"
  cluster_type              = "multi-node"
  number_of_nodes           = 3
  cluster_subnet_group_name = aws_redshift_subnet_group.data_pipeline.name
  publicly_accessible       = true
  encrypted                 = false
  skip_final_snapshot       = true

  tags = {
    Name        = "analytics-warehouse"
    Environment = "production"
  }
}
