module "vpc" {
  source = "github.com/opensupplyhub/terraform-aws-vpc?ref=7.0.6"

  name                       = "vpc${local.short}"
  region                     = var.aws_region
  key_name                   = var.aws_key_name
  cidr_block                 = var.vpc_cidr_block
  private_subnet_cidr_blocks = var.vpc_private_subnet_cidr_blocks
  public_subnet_cidr_blocks  = var.vpc_public_subnet_cidr_blocks
  availability_zones         = var.aws_availability_zones
  bastion_ami                = var.bastion_ami
  bastion_instance_type      = var.bastion_instance_type

  # OSDEV-3531: lets the SSM agent register the bastion with Session Manager.
  bastion_iam_instance_profile = aws_iam_instance_profile.bastion.name

  project     = var.project
  environment = var.environment
}

