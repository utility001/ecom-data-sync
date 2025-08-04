# Create IAM ROLE with trust policy
resource "aws_iam_role" "redshift-role" {
  name = "${var.project_name}-redshift-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AssumeRedshiftRole"
        Effect = "Allow"
        Action = ["sts:AssumeRole"]
        Principal = {
          Service = ["redshift.amazonaws.com"]
        }
      },
    ]
  })
}

# create permission policy for your iam role
resource "aws_iam_role_policy" "redshift-policy" {
  name = "${var.project_name}-redshift-policy"
  role = aws_iam_role.redshift-role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadDataFromS3"
        Effect   = "Allow"
        Action   = ["s3:ListBucket", "s3:GetObject"]
        Resource = ["arn:aws:s3:::ecom-data-sync*"]
      },
    ]
  })
}

resource "random_password" "redshift-password" {
  length           = 16
  override_special = "()!#$%&_+-={}|" # A list of specital characters that will be used in creating the password
  special          = true
  numeric          = true
  upper            = true
  lower            = true
}

#     secret_name             = "ecomdatasync/dev/redshift-admin-creds/"
#     recovery_window_in_days = 0
#     admin_username          = "ecomdatasync_admin"

resource "aws_secretsmanager_secret" "redshift-admin-secrets" {
  name                    = "${var.project_name}/${var.environment}/redshift-admin-credentials"
  description             = "Admin credentials for the redshift cluster"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "redshift_admin_secrets_version" {
  secret_id = aws_secretsmanager_secret.redshift-admin-secrets.id
  secret_string = jsonencode({
    username = "${var.project_name}_admin"
    password = random_password.redshift-password.result
  })
}


#  name                = "ecomdatasync-redshift-sg"
#     ingress_cidr        = "0.0.0.0/0"
#     ingress_from_port   = 5439
#     ingress_to_port     = 5439
#     ingress_ip_protocol = "tcp"
#     egress_cidr         = "0.0.0.0/0"
#     egress_ip_protocol  = "-1"

# Redshift security group
resource "aws_security_group" "redshift-security-group" {
  name   = "${var.project_name}-redshift-security-group"
  vpc_id = aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "redshift-ingress-rule" {
  security_group_id = aws_security_group.redshift-security-group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 5439
  ip_protocol       = "tcp"
  to_port           = 5439
}

resource "aws_vpc_security_group_egress_rule" "redshift-egress-rule" {
  security_group_id = aws_security_group.redshift-security-group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}


# Define redshift subnet group
resource "aws_redshift_subnet_group" "redshift-subnet-group" {
  name       = "${var.project_name}-redshift-subnet-group"
  subnet_ids = [aws_subnet.public-subnet.id]
}

resource "aws_redshift_parameter_group" "redshfit-param-group" {
  name   = "${var.project_name}-redshift-param-group"
  family = "redshift-2.0"

  parameter {
    name  = "require_ssl"
    value = false
  }
}


resource "aws_redshift_cluster" "redshift_cluster" {
  cluster_identifier           = "${var.project_name}-${var.environment}-cluster"
  database_name                = "transactions"
  master_username              = "${var.project_name}_admin"
  master_password              = random_password.redshift-password.result
  node_type                    = "ra3.large"
  cluster_type                 = "multi-node"
  number_of_nodes              = 2
  publicly_accessible          = true
  port                         = 5439
  encrypted                    = true
  skip_final_snapshot          = true
  iam_roles                    = [aws_iam_role.redshift-role.arn]
  cluster_subnet_group_name    = aws_redshift_subnet_group.redshift-subnet-group.name
  vpc_security_group_ids       = [aws_security_group.redshift-security-group.id]
  cluster_parameter_group_name = aws_redshift_parameter_group.redshfit-param-group.name
}