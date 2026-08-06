# Modified from azavea/terraform-aws-ecr-repository to add image_tag_mutability
# (and expose scan_on_push, which upstream hardcoded).
variable "repository_name" {
  type        = string
  description = "Name of the repository"
}

variable "image_tag_mutability" {
  type        = string
  default     = "IMMUTABLE"
  description = "The tag mutability setting for the repository. Must be one of MUTABLE or IMMUTABLE, all current call-sites set this explicitly."

  validation {
    condition     = contains(["MUTABLE", "IMMUTABLE"], var.image_tag_mutability)
    error_message = "image_tag_mutability must be either MUTABLE or IMMUTABLE."
  }
}

variable "scan_on_push" {
  type        = bool
  default     = true
  description = "If true, images are scanned for vulnerabilities after being pushed to the repository."
}

variable "attach_lifecycle_policy" {
  default     = false
  type        = bool
  description = "If true, an ECR lifecycle policy will be attached"
}

variable "lifecycle_policy" {
  default     = ""
  type        = string
  description = "Contents of the ECR lifecycle policy"
}
