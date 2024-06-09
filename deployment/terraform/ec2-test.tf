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

resource "aws_security_group" "ec2_security_group" {
  vpc_id = module.vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ec2-test-security-group"
  }
}

resource "aws_security_group_rule" "allow_ec2_to_opensearch" {
  type                     = "ingress"
  from_port                = 9200
  to_port                  = 9200
  protocol                 = "tcp"
  security_group_id        = aws_security_group.opensearch.id
  source_security_group_id = aws_security_group.ec2_security_group.id
}

resource "aws_instance" "example_server" {
  count         = length(module.vpc.private_subnet_ids)
  ami           = data.aws_ami.latest_amazon_linux.id 
  instance_type = "t2.micro"
  subnet_id     = module.vpc.private_subnet_ids[count.index]

  security_groups = [
    aws_security_group.ec2_security_group.name,
  ]

  tags = {
    Name = "EC2Test"
  }
}
