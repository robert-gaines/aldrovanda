terraform {
    required_providers {
        digitalocean = {
            source  = "digitalocean/digitalocean"
            version = "~> 2.0"
        }
        cloudflare = {
            source  = "cloudflare/cloudflare"
            version = "~> 5"
        }
    }
}

variable "DIGITAL_OCEAN_TOKEN" {
    description = "The token for the DigitalOcean provider"
    type        = string
}

provider "digitalocean" {
    token = var.DIGITAL_OCEAN_TOKEN
}

provider "cloudflare" {
    api_token = var.CLOUDFLARE_KEY
}

variable "regions" {
    description = "List of regions to create droplets in"
    type        = list(string)
    default     = ["sfo3"]
}

variable "CLOUDFLARE_KEY" {
    description = "Cloudflare API Token"
    type        = string
}

variable "CLOUDFLARE_ZONE" {
    description = "Cloudflare Zone ID"
    type        = string
}

variable "ssh_public_key" {
    description = "SSH Public Key"
    type        = string
}

resource "digitalocean_ssh_key" "default" {
  name       = "digital_ocean"
  public_key = var.ssh_public_key
}

resource "digitalocean_project" "aldrovanda" {
  name        = "aldrovanda"
  description = "Samba Honeypots"
  purpose     = "Research"
  environment = "Production"
}

resource "digitalocean_droplet" "honeypot" {
    count  = length(var.regions) * 1
    name   = "aldrovanda${count.index}"
    region = var.regions[count.index % length(var.regions)]
    size   = "s-1vcpu-1gb"
    image  = "ubuntu-24-04-x64"
    ssh_keys = [digitalocean_ssh_key.default.id]

    provisioner "remote-exec" {
        inline = [
            "while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do echo 'Waiting for dpkg lock...'; sleep 5; done",
            "while sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do echo 'Waiting for apt lock...'; sleep 5; done",
            "sudo apt-get update",
            "sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -",
            "sudo add-apt-repository -y 'deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable'",
            "sudo apt-get update",
            "sudo apt-get install -y docker-ce",
            "sudo systemctl start docker",
            "sudo systemctl enable docker",
            "sudo docker run -d -p 80:80 -p 139:139 -p 445:445 robertgaines/aldrovanda:latest"
        ]

        connection {
            type        = "ssh"
            user        = "root"
            private_key = file("/keys/digital_ocean")
            host        = self.ipv4_address
        }

    }
}

resource "digitalocean_project_resources" "aldrovanda_resources" {
  project = digitalocean_project.aldrovanda.id
  resources = [
    for droplet in digitalocean_droplet.honeypot :  "do:droplet:${droplet.id}"
  ]
}

resource "cloudflare_dns_record" "honeypot" {
  count   = length(digitalocean_droplet.honeypot)
  zone_id = var.CLOUDFLARE_ZONE
  name    = "aldrovanda${count.index}"
  type    = "A"
  comment = "Aldrovanda honeypot # ${count.index}"
  content = digitalocean_droplet.honeypot[count.index].ipv4_address
  ttl     = 300
}

output "droplet_ips" {
  value = [for droplet in digitalocean_droplet.honeypot : droplet.ipv4_address]
}