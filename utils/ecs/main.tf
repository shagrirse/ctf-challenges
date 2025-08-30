terraform {
  required_version = ">= 1.0"
}

provider "aws" {
  region = "ap-southeast-1"
}

locals {
  challenge_name_set = toset(var.challenge_names)
}

resource "aws_lb" "ctf_alb" {
  name               = "${var.event_name}-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = module.vpc.public_subnets
  security_groups    = [aws_security_group.alb.id]
}

# Load balancer for all HTTP:80 requests
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.ctf_alb.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Not found"
      status_code  = "404"
    }
  }
}

# Loop over challenges
resource "aws_ecs_cluster" "ctf" {
  name = "${var.event_name}-cluster"
}

resource "aws_ecs_task_definition" "challenge" {
  for_each = local.challenge_name_set

  family                   = "${var.event_name}-${each.value}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  container_definitions = jsonencode([
    {
      name      = each.value
      image     = var.ecr_image_uris[each.value]
      essential = true
      portMappings = [
        {
          containerPort = tonumber(var.port_protocol[each.value]["port"])
          protocol      = "tcp"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "challenge" {
  for_each = local.challenge_name_set

  name            = "${var.event_name}-${each.value}"
  cluster         = aws_ecs_cluster.ctf.id
  task_definition = aws_ecs_task_definition.challenge[each.value].arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.challenge[each.value].arn
    container_name   = each.value
    container_port   = tonumber(var.port_protocol[each.value]["port"])
  }
  depends_on = [aws_lb_listener.http]
}

resource "aws_lb_target_group" "challenge" {
  for_each    = local.challenge_name_set
  name        = "tg-${each.value}"
  port        = tonumber(var.port_protocol[each.value]["exposed_port"])
  protocol    = var.port_protocol[each.value]["protocol"]
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"
  health_check {
    path                = "/"
    protocol            = var.port_protocol[each.value]["protocol"]
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener_rule" "challenge" {
  for_each     = local.challenge_name_set
  listener_arn = aws_lb_listener.http.arn
  priority     = 100 + index(var.challenge_names, each.value)
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.challenge[each.value].arn
  }
  condition {
    host_header {
      values = ["${each.value}.${var.domain_name}"]
    }
  }
}

resource "aws_route53_record" "challenge" {
  for_each = local.challenge_name_set
  zone_id  = var.hosted_zone_id
  name     = "${each.value}.${var.domain_name}"
  type     = "A"
  alias {
    name                   = aws_lb.ctf_alb.dns_name
    zone_id                = aws_lb.ctf_alb.zone_id
    evaluate_target_health = true
  }
}