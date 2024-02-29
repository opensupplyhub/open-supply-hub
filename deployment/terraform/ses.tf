resource "aws_ses_domain_identity" "app" {
  domain = local.domain_name
}

resource "aws_ses_domain_dkim" "app" {
  domain = aws_ses_domain_identity.app.domain
}

