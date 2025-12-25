
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.8.0"
    }
    template = {
      source  = "hashicorp/template"
      version = "~> 2.2.0"
    }
    kafka = {
      source = "zywillc/kafka"
      version = "1.0.1"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }
}
