#
# ACM resources
#
module "cert_cdn" {
  source = "github.com/azavea/terraform-aws-acm-certificate?ref=4.0.0"

  providers = {
    aws.acm_account     = aws.certificates
    aws.route53_account = aws
  }

  domain_name               = local.domain_name
  subject_alternative_names = ["*.${local.domain_name}"]
  hosted_zone_id            = data.aws_route53_zone.external.zone_id
  validation_record_ttl     = "60"
}

module "cert_lb" {
  source = "github.com/azavea/terraform-aws-acm-certificate?ref=4.0.0"

  providers = {
    aws.acm_account     = aws
    aws.route53_account = aws
  }

  domain_name               = local.domain_name
  subject_alternative_names = ["*.${local.domain_name}"]
  hosted_zone_id            = data.aws_route53_zone.external.zone_id
  validation_record_ttl     = "60"
}

