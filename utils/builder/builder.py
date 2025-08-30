from pathlib import Path
from collections import defaultdict
import configparser
import os
import yaml
import subprocess
import docker
import json
import re

class Builder():
  def __init__(self):
    self.rootFolder = Path(__file__).parent.parent.parent
    self.configFilePath = str(Path(__file__).parent.parent) + '/config.ini'

    config = configparser.ConfigParser()
    config.read(self.configFilePath)
    self.config = config

    self.repositoryUri = self.config['ECR']['base_repository_uri']
    self.repoName = self.config['ECR']['REPO_NAME']

  def login_aws_docker(self, ecr_uri):
    region = "ap-southeast-1"

    # Run the AWS CLI to get the ECR login password and pipe it to docker login
    aws_cmd = ["aws", "ecr", "get-login-password", "--region", region]
    docker_cmd = ["docker", "login", "--username", "AWS", "--password-stdin", ecr_uri]

    # Get the password from AWS CLI
    proc = subprocess.run(aws_cmd, capture_output=True, check=True)
    password = proc.stdout

    # Pipe the password to docker login
    subprocess.run(docker_cmd, input=password, check=True)

  def add_pushed_challenge_config(self, challenge_name, repository, port, protocol, exposed_port):
    # Record challenge_name and repository in terraform.tfvars.json
    tfvars_path = self.rootFolder / 'utils' / 'ecs' / 'terraform.tfvars.json'
    tfvars = {}
    if tfvars_path.exists():
      with open(tfvars_path, 'r') as f:
        try:
          tfvars = yaml.safe_load(f) or {}
        except Exception:
          tfvars = {}

    # Ensure keys exist
    tfvars.setdefault('challenge_names', [])
    tfvars.setdefault('ecr_image_uris', defaultdict(dict))
    tfvars.setdefault('port_protocol', defaultdict(dict))

    if challenge_name not in tfvars['challenge_names']:
      tfvars['challenge_names'].append(challenge_name)
    if repository not in tfvars['ecr_image_uris']:
      tfvars['ecr_image_uris'][challenge_name] = repository
    if challenge_name not in tfvars['port_protocol']:
      tfvars['port_protocol'][challenge_name] = {
        "port": port,
        "protocol": protocol,
        "exposed_port": exposed_port
      }
    
    # Write back as JSON
    with open(tfvars_path, 'w+') as f:
      json.dump(tfvars, f, indent=2)

  def build_push_docker_image(self, challenge_name, path, port, protocol, exposed_port):
    try:
      if not re.match(r'^[A-Za-z0-9\-]+$', challenge_name):
        raise Exception('Challenge name does not follow conventions. Please only include alphanumeric characters and hyphens if spaces are needed.')
      client = docker.from_env()
      repoName = self.repoName

      # Build image from dockerfile
      image, build_log = client.images.build(path=str(path), tag=repoName, rm=True, quiet=False, nocache=False)

      # Configs/auth
      baseUri = self.repositoryUri
      repository = f'{baseUri}:{challenge_name}'

      # Tag ECR image
      image.tag(repository=repository)
      # Push image to ECR
      response = client.api.push(f'{baseUri}:{challenge_name}')
      self.add_pushed_challenge_config(challenge_name, repository, port, protocol, exposed_port)
    except Exception as e:
      print(f"[{challenge_name}] Error creating image: {e}")
      return None

  def build_challenges(self):
    # Login and prep docker/aws for push
    self.login_aws_docker(self.repositoryUri.replace(f'/{self.repoName}', ''))

    categories = [cat.strip() for cat in self.config.get('CTF', 'categories').split(',')]
    challengeRootFolder = self.rootFolder
    
    challengePaths = []

    dockerChallenges = defaultdict(list)
    textChallenges = defaultdict(list)
    otherChallenges = defaultdict(list)

    # Iterate through each category specified in configuration file
    for category in categories:
      categoryDirectory = challengeRootFolder / category
      if not categoryDirectory.exists():
        continue
      # Iterate through every challenge in each category
      # Determine the challenge type and build accordingly.
      for challengeDirectory in os.listdir(categoryDirectory):
        challenge_path = categoryDirectory / challengeDirectory / 'challenge.yml'
        if not challenge_path.exists():
          continue
        try:
          with open(challenge_path) as file:
            data = yaml.safe_load(file)
          if data.get('challenge_type') == 'docker':
            port = data.get('port_number')
            protocol = (data.get('protocol')).upper()
            exposed_port = data.get('exposed_port_number')
            if (not(port) or not(protocol) or protocol not in ['GENEVE', 'HTTP', 'HTTPS', 'TCP', 'TCP_UDP', 'TLS', 'UDP']):
              raise Exception('Port or protocol not specified for this challenge, or protocol is invalid (accepts GENEVE, HTTP, HTTPS, TCP, TCP_UDP, TLS, or UDP only).')
            challengeName = data.get('name')
            self.build_push_docker_image(challengeName, str(categoryDirectory / challengeDirectory), port, protocol, exposed_port)
            dockerChallenges[category].append(challengeName)
          elif data.get('challenge_type') == 'text':
            textChallenges[category].append(challengeDirectory)
          else:
            otherChallenges[category].append(challengeDirectory)
          challengePaths.append(f'{category}/{challengeDirectory}')
        except Exception as e:
          print(f"Error reading {challenge_path}: {e}")
      # Add ALL challenges to the ctfd configuration file
    self.add_challenges_to_ctfd(challengePaths)
    # Programatically add all challenges using the ctfcli command
    subprocess.run(['ctf', 'challenge', 'install'])
    
    return dict(dockerChallenges), dict(textChallenges), dict(otherChallenges)

  def add_challenges_to_ctfd(self, path_list):
    ctfdConfigPath = f'{self.rootFolder}/.ctf/config'
    ctfdConfig = configparser.ConfigParser()
    ctfdConfig.read(ctfdConfigPath)
    for path in path_list:
      ctfdConfig.set('challenges', path, path)
    
    with open(ctfdConfigPath, 'w+') as file:
      ctfdConfig.write(file)
    return True
print(Builder().build_challenges())