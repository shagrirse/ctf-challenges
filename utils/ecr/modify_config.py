import configparser
import os

def main():
  add_config_path = 'add_to_config.txt'
  config_path = '../config.ini'
  section = 'ECR'
  option = 'base_repository_uri'

  # Check if add_to_config.txt exists
  if not os.path.isfile(add_config_path):
    print(f"Error: {add_config_path} does not exist.")
    return

  # Read key-value from add_to_config.txt
  try:
    with open(add_config_path, 'r') as file:
      line = file.readline().strip()
      if '=' not in line:
        print("Error: No '=' found in the line.")
        return
      key, _, value = line.partition("=")
      if not key or not value:
        print("Error: Key or value missing.")
        return
  except Exception as e:
    print(f"Error reading {add_config_path}: {e}")
    return

  # Read config.ini
  config = configparser.ConfigParser()
  if not os.path.isfile(config_path):
    print(f"Error: {config_path} does not exist.")
    return
  try:
    config.read(config_path)
    if section not in config:
      print(f"Error: Section '{section}' not found in {config_path}.")
      return
    config.set(section, option, value.strip().replace('"', ''))
    with open(config_path, 'w') as config_file:
      config.write(config_file)
  except Exception as e:
    print(f"Error modifying {config_path}: {e}")
    return

  # Remove add_to_config.txt
  try:
    os.remove(add_config_path)
  except Exception as e:
    print(f"Error removing {add_config_path}: {e}")

if __name__ == '__main__':
  main()