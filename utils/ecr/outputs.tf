output "base_repository_uri" {
  value = aws_ecr_repository.ecr_repository.repository_url
}