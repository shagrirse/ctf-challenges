variable "domain_name" {
  description = "Base domain for CTF event"
  type        = string
}

variable "challenge_names" {
  description = "List of challenge names"
  type        = list(string)
}

variable "ecr_image_uris" {
  description = "Map of challenge name to ECR image URI"
  type        = map(string)
}

variable "hosted_zone_id" {
  description = "Route 53 hosted zone ID"
  type        = string
}

variable "event_name" {
  description = "Name of the CTF event"
  type        = string
}

variable "port_protocol" {
  description = "Map of challenges and their port/protocol"
  type        = map(map(string))
}