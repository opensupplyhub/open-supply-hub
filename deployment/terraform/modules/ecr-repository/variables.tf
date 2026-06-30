variable "repository_name" {
  type        = string
  description = "Name of the repository"
}

variable "image_tag_mutability" {
  type        = string
  default     = "MUTABLE"
  description = "The tag mutability setting for the repository. Must be one of MUTABLE or IMMUTABLE."

  validation {
    condition     = contains(["MUTABLE", "IMMUTABLE"], var.image_tag_mutability)
    error_message = "image_tag_mutability must be either MUTABLE or IMMUTABLE."
  }
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
