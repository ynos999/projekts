terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.56.0"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

# New server
resource "hcloud_server" "projects" {
  name        = "projects"
  server_type = "cx23"
  image       = "ubuntu-22.04"
  location    = "hel1"

  # Ja jaunu SSh atslēgu liek projektā
  #  ssh_keys    = [hcloud_ssh_key.default.id]

  # izmanto jau esošu SSH key Hetzner panelī
  ssh_keys = ["Edijs"]

  labels = {
    project = "projects"
    env     = "prod"
  }

  user_data = templatefile("cloud-init/projects.yml", {
    ssh_user       = var.ssh_user
    ssh_public_key = file(var.ssh_public_key)
  })
}

resource "hcloud_firewall" "projects" {
  name = "projects-fw"

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "22"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
    description = "SSH access"
  }
}

resource "hcloud_firewall_attachment" "projects" {
  firewall_id = hcloud_firewall.projects.id
  server_ids  = [hcloud_server.projects.id]
}