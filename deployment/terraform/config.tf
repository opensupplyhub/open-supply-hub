provider "aws" {
  region = var.aws_region
  default_tags {
    tags = local.default_tags
  }
}

/**
* To use an ACM Certificate with Amazon CloudFront, you must
* request or import the certificate in the US East (N. Virginia) region.
* ACM Certificates in this region that are associated with a CloudFront
* distribution are distributed to all the geographic locations configured
* for that distribution.
*
* https://docs.aws.amazon.com/acm/latest/userguide/acm-regions.html
*/
provider "aws" {
  alias  = "certificates"
  region = "us-east-1"

  default_tags {
    tags = local.default_tags
  }
}

/**
* Route 53 public hosted zone query logging requires both the CloudWatch Logs
* log group and the CloudWatch Logs resource policy that authorises Route 53 to
* write into it to live in the US East (N. Virginia) region, whatever region
* the rest of the stack runs in.
*
* https://docs.aws.amazon.com/Route53/latest/APIReference/API_CreateQueryLoggingConfig.html
*/
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = local.default_tags
  }
}

provider "template" {
}

terraform {
  backend "s3" {
    region  = "eu-west-1"
    encrypt = "true"
  }
}

# Ensures every new EBS volume (and therefore every snapshot taken from it) in
# this account/region is encrypted by default, without requiring encryption
# settings on individual resources (e.g. the VPN EC2 instance or the AWS Batch
# Spot compute environments, none of which set this explicitly today).
resource "aws_ebs_encryption_by_default" "this" {
  enabled = true
}

