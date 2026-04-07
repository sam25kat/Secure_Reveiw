variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "account_id" {
  description = "AWS account ID for the management account"
  type        = string
}

variable "dev_account_id" {
  description = "AWS account ID for the development account"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "management"
}
