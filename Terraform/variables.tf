variable "hcloud_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "ssh_user" {
  description = "SSH lietotāja vārds serveriem"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH publiskās atslēgas fails"
  type        = string
}

variable "ssh_keys" {
  description = "SSH keys no Hetzner Cloud"
  type        = list(string)
}