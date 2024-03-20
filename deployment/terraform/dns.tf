#
# Private DNS resources
#
resource "aws_route53_zone" "internal" {
  name = var.r53_private_hosted_zone

  vpc {
    vpc_id     = module.vpc.id
    vpc_region = var.aws_region
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_route53_record" "database" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "database.service.${var.r53_private_hosted_zone}"
  type    = "CNAME"
  ttl     = "10"
  records = [module.database_enc.hostname]
}

resource "aws_route53_record" "cache" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "cache.service.${var.r53_private_hosted_zone}"
  type    = "CNAME"
  ttl     = "10"
  records = [aws_elasticache_cluster.memcached.cluster_address]
}

#
# Public DNS resources
#
# resource "aws_route53_zone" "external" {
#   name = var.r53_public_hosted_zone
# }



data "aws_route53_zone" "external" {
  name = var.r53_public_hosted_zone
}
locals {
  domain_name= var.environment == "Development" ? "dev.${var.r53_public_hosted_zone}" : var.environment == "Staging" ? "${var.r53_public_hosted_zone}" : var.environment == "Production" ? "${var.r53_public_hosted_zone}" : "${lower(var.environment)}.${var.r53_public_hosted_zone}"
}
resource "aws_route53_record" "bastion" {
  zone_id = data.aws_route53_zone.external.zone_id
  name    = "bastion.${local.domain_name}"
  type    = "CNAME"
  ttl     = "300"
  records = [module.vpc.bastion_hostname]
}

resource "aws_route53_record" "origin" {
  zone_id = data.aws_route53_zone.external.zone_id
  name    = "origin.${local.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.app.dns_name
    zone_id                = aws_lb.app.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.external.zone_id
  name    = local.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.cdn.domain_name
    zone_id                = aws_cloudfront_distribution.cdn.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www_ipv6" {
  zone_id = data.aws_route53_zone.external.zone_id
  name    = local.domain_name
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.cdn.domain_name
    zone_id                = aws_cloudfront_distribution.cdn.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "ses_verification" {
  zone_id = data.aws_route53_zone.external.zone_id
  name    = "_amazonses.${local.domain_name}"
  type    = "TXT"
  ttl     = "300"
  records = [aws_ses_domain_identity.app.verification_token]
}

resource "aws_route53_record" "ses_dkim" {
  count   = 3
  zone_id = data.aws_route53_zone.external.zone_id
  name    = "${element(aws_ses_domain_dkim.app.dkim_tokens, count.index)}._domainkey.${local.domain_name}"
  type    = "CNAME"
  ttl     = "300"
  records = ["${element(aws_ses_domain_dkim.app.dkim_tokens, count.index)}.dkim.amazonses.com"]
}

resource "aws_service_discovery_private_dns_namespace" "service_discovery" {
  name        = var.r53_service_discovery_zone
  description = "app service discovery"
  vpc         = module.vpc.id
}

resource "aws_service_discovery_service" "app" {
  name = "api"
  dns_config {
    namespace_id   = aws_service_discovery_private_dns_namespace.service_discovery.id
    routing_policy = "MULTIVALUE"
    dns_records {
      ttl  = 10
      type = "A"
    }
  }
  health_check_custom_config {
    failure_threshold = 5
  }

  # Remove after https://github.com/terraform-providers/terraform-provider-aws/issues/4853 is resolved
  provisioner "local-exec" {
    when = destroy
    command = "${path.module}/servicediscovery-drain.sh ${self.id}"
  }
}
