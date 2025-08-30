cd ecr
terraform apply -var-file=./terraform.tfvars
terraform output > add_to_config.txt
python3 modify_config.py
cd ../builder
python3 builder.py