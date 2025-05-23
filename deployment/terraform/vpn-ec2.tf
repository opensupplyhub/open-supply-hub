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

data "template_file" "wireguard_compose" {
  count    = var.environment == "Rba" ? 1 : 0
  template = file("${path.module}/wireguard/docker-compose.yml")
  vars = {
    wg_host = var.environment == "Rba" ? aws_eip.vpn_eip[0].public_ip : ""
  }
}

resource "aws_instance" "vpn_ec2" {
  count         = var.environment == "Rba" ? 1 : 0
  ami           = data.aws_ami.aws_ami_vpn_ec2.id
  instance_type = "t4g.nano"
  subnet_id     = module.vpc.public_subnet_ids[count.index]

  associate_public_ip_address = true
  key_name                    = var.aws_key_name
  iam_instance_profile        = aws_iam_instance_profile.vpn_instance.name

  vpc_security_group_ids = [aws_security_group.vpn_sg.id]

  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Install Docker and Docker Compose
    sudo yum update -y
    sudo yum install -y docker
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker ec2-user
    sudo mkdir -p /usr/libexec/docker/cli-plugins
    sudo curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-aarch64 \
      -o /usr/libexec/docker/cli-plugins/docker-compose
    sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose

    # Create directory for WireGuard
    sudo mkdir -p /opt/wireguard
    cd /opt/wireguard

    # Create docker-compose.yml with the correct WG_HOST
    cat > docker-compose.yml << 'EOC'
    ${data.template_file.wireguard_compose[0].rendered}
    EOC

    # Start WireGuard
    sudo docker compose up -d
  EOF

  tags = {
    Name        = "Bastion-vpn-ec2-${var.environment}"
    Environment = var.environment
    Service     = "vpn"
  }
}

resource "aws_security_group" "vpn_sg" {
  name        = "vpn-ec2-sg-${var.environment}"
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
  count  = var.environment == "Rba" ? 1 : 0
  domain = "vpc"
  tags = {
    Name        = "vpn-eip-${var.environment}"
    Environment = var.environment
    Service     = "vpn"
  }
}

resource "aws_eip_association" "eip_assoc" {
  count         = var.environment == "Rba" ? 1 : 0
  instance_id   = aws_instance.vpn_ec2[0].id
  allocation_id = aws_eip.vpn_eip[0].id
}
