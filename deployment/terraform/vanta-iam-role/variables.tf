variable "vanta_assumed_role_external_ids" {
  type      = list(any)
  default   = []
  sensitive = true
}

variable "vanta_assumed_role_principals" {
  type      = list(any)
  default   = []
  sensitive = true
}
