## Hetzner cloud create 1 nodes
### 1. Create file terraform.tfvars and add 
##
hcloud_token = "YourToken"
ssh_user = "YourUser"
ssh_public_key = "~/.ssh/id_rsa.pub"
##
### If You need edit cloud-init master and worker files.
###
### Terraform commands:
### terraform init
### terraform plan
### terraform apply

### mkdir "$env:USERPROFILE\.ssh"
### ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa"
### public_key for Windows = file("C:/Users/YourUser/.ssh/id_rsa.pub")

### public_key for Linux is "~/.ssh/id_rsa.pub"
### Test cloud init
### cloud-init status --long
### id ${ssh_user}
### docker ps
### cd ~/.ssh
### cat github_actions.pub >> authorized_keys
### github_actions.pub: command not found
### chmod 600 authorized_keys