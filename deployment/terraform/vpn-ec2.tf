data "aws_ami" "aws_ami_vpn_ec2" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "architecture"
    values = ["arm64"]
  }
  filter {
    name   = "name"
    values = ["al2023-ami-2023*"]
  }
}

data "aws_iam_policy_document" "vpn_instance_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "vpn_instance" {
  name               = "vpn${local.short}InstanceRole"
  assume_role_policy = data.aws_iam_policy_document.vpn_instance_assume_role.json
}

resource "aws_iam_role_policy_attachment" "vpn_instance_ssm" {
  role       = aws_iam_role.vpn_instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "vpn_instance" {
  name = aws_iam_role.vpn_instance.name
  role = aws_iam_role.vpn_instance.name
}

# TODO: create only for RBA environment
resource "aws_instance" "vpn_ec2" {
  count         = var.environment == "Development" ? 1 : 0
  ami           = data.aws_ami.aws_ami_vpn_ec2.id
  instance_type = "t4g.nano"
  subnet_id     = module.vpc.public_subnet_ids[count.index]

  associate_public_ip_address = true
  key_name                    = var.aws_key_name
  iam_instance_profile        = aws_iam_instance_profile.vpn_instance.name

  vpc_security_group_ids = [aws_security_group.vpn_sg.id]

  tags = {
    Name        = "Bastion-vpn-ec2-${var.environment}"
    Environment = var.environment
    Service     = "vpn"
  }

  /*
  lifecycle {
    prevent_destroy = true
  }
  */
}

resource "aws_security_group" "vpn_sg" {
  name        = "vpn-ec2-sg"
  description = "Allow WireGuard UDP traffic"
  vpc_id      = module.vpc.id

  ingress {
    from_port   = 51820
    to_port     = 51820
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "WireGuard VPN access"
  }

  ingress {
    from_port   = 51821
    to_port     = 51821
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "WireGuard management access (WebUI)"
  }

  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [module.vpc.bastion_security_group_id]
    description     = "SSH access from bastion host only"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "vpn-sg-${var.environment}"
    Environment = var.environment
    Service     = "vpn"
  }
}

resource "aws_eip" "vpn_eip" {
  count  = var.environment == "Development" ? 1 : 0
  domain = "vpc"
}

resource "aws_eip_association" "eip_assoc" {
  count         = var.environment == "Development" ? 1 : 0
  instance_id   = aws_instance.vpn_ec2[0].id
  allocation_id = aws_eip.vpn_eip[0].id
}
