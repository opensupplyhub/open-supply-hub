data "aws_ami" "latest_amazon_linux" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["amazon"]
}

resource "aws_instance" "test-ec2-instance" {
  count         = length(module.vpc.private_subnet_ids)
  ami           = data.aws_ami.latest_amazon_linux.id 
  instance_type = "t2.micro"
  subnet_id     = module.vpc.private_subnet_ids[count.index]

  security_groups = [
    aws_security_group.ec2_security_group.id,
  ]

  depends_on = [
    aws_security_group.ec2_security_group,
    aws_security_group_rule.allow_ec2_to_opensearch,
  ]

  tags = {
    Name = "EC2Test"
  }
}
