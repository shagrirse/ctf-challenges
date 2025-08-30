resource "aws_ecr_repository" "ecr_repository" {
  name                 = var.repo_name
  image_tag_mutability = "MUTABLE"
  region = var.aws_region

  image_scanning_configuration {
    scan_on_push = true
  }
}