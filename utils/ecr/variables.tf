variable "repo_name" {
  type = string
  default = "example_repo"
  description = "ECR Repository Name in AWS"
}

variable "aws_region" {
  type        = string
  description = "Region to deploy the AWS resource to"
  default     = "ap-southeast-1"
}