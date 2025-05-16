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

# TODO: create only for RBA environment, Development is for testing
resource "aws_instance" "vpn_ec2" {
  count         = var.environment == "Development" ? 1 : 0
  ami           = data.aws_ami.aws_ami_vpn_ec2.id
  instance_type = "t4g.nano"
  subnet_id = module.vpc.public_subnet_ids[count.index]

  associate_public_ip_address = true
  key_name                    = var.aws_key_name

  vpc_security_group_ids = [aws_security_group.vpn_sg.id]

  tags = {
    Name = "vpn_ec2"
  }

  # TODO: Enable this rule once WireGuard setup
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
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # TODO: change later
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "vpn-sg"
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
