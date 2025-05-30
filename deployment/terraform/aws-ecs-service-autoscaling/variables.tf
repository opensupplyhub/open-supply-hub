variable "name_prefix" {
  description = "Name prefix for resources on AWS"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Resource tags"
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
}

variable "ecs_service_name" {
  description = "Name of the ECS service"
}

variable "max_cpu_threshold" {
  description = "Threshold for max CPU usage"
  default     = 85
  type        = number
}

variable "min_cpu_threshold" {
  description = "Threshold for min CPU usage"
  default     = 10
  type        = number
}

variable "max_cpu_evaluation_period" {
  description = "The number of periods over which data is compared to the specified threshold for max cpu metric alarm"
  default     = 3
  type        = number
}

variable "min_cpu_evaluation_period" {
  description = "The number of periods over which data is compared to the specified threshold for min cpu metric alarm"
  default     = 3
  type        = number
}

variable "max_cpu_period" {
  description = "The period in seconds over which the specified statistic is applied for max cpu metric alarm"
  default     = 60
  type        = number
}
variable "min_cpu_period" {
  description = "The period in seconds over which the specified statistic is applied for min cpu metric alarm"
  default     = 60
  type        = number
}

variable "scale_target_max_capacity" {
  description = "The max capacity of the scalable target"
  default     = 5
  type        = number
}

variable "scale_target_min_capacity" {
  description = "The min capacity of the scalable target"
  default     = 1
  type        = number
}

variable "sns_topic_arn" {
  type        = string
  description = "The ARN of an SNS topic to send notifications on alarm actions."
  default     = ""
}

variable "cooldown_scale_up" {
  description = "Cooldown period for scaling actions"
  type        = number
  default     = 60
}

variable "cooldown_scale_down" {
  description = "Cooldown period for scaling actions"
  type        = number
  default     = 60
}
