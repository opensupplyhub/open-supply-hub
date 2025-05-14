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
  count = var.environment == "Development" ? 1 : 0
  ami = data.aws_ami.aws_ami_vpn_ec2.id
  instance_market_options {
    market_type = "spot"
    spot_options {
      max_price = 0.0031
    }
  }
  vpc_security_group_ids = [aws_security_group.vpn_sg.id]
  instance_type = "t4g.nano"
  tags = {
    Name = "vpn_ec2"
  }
}

resource "aws_security_group" "vpn_sg" {
  name        = "vpn-ec2-sg"
  description = "Allow WireGuard UDP traffic"
  vpc_id      = module.vpc.id

  ingress {
    from_port   = 51820
    to_port     = 51820
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"] # TODO: restrict to known IPs
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

# Static IP address, which is reachable from the internet
resource "aws_eip" "vpn_eip" {
  count  = var.environment == "Development" ? 1 : 0
  domain = "vpc"
}

resource "aws_eip_association" "eip_assoc" {
  count         = var.environment == "Development" ? 1 : 0
  instance_id   = aws_instance.vpn_ec2[0].id
  allocation_id = aws_eip.vpn_eip[0].id
}

# TODO:
# 1. Configure security groups, open ports for WireGuard with Custom UDP type, define port range.
# 2. Create access keys to connect to the instance if needed.
# 3. Obtain (or create) external IP-address and associate it with instance.
# 4. Install WireGuard in EC2 instance (example https://github.com/pprometey/wireguard_aws), probably bash script required.
# 5. Forward requests that set in ip_whitelist to specific ECS instance.
