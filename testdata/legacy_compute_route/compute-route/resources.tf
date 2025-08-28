provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  description = "Default network for the project"
  auto_create_subnetworks = true
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.disks.diskEncryptionKey.rawKey: ['SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0=']
#
#tfimport-terraform import google_compute_instance.compute_instance  __project__/us-west1-a/compute-instance
resource "google_compute_instance" "compute_instance" {
  provider = google-beta

  name = "compute-instance"
  can_ip_forward = true
  zone = "us-west1-a"
  machine_type = "n1-standard-1"
  labels = {
    created-from = "disk"
    network-type = "global"
  }
  boot_disk {
    device_name = "proxycontroldisk"
    mode = "READ_ONLY"
    disk_encryption_key_raw = "SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0="
    source = google_compute_disk.compute_disk.id
    auto_delete = false
  }
  network_interface {
    network_ip = "10.2.0.4"
    network = google_compute_network.compute_network.id
  }
}

#tfimport-terraform import google_compute_route.compute_route  __project__/compute-route
resource "google_compute_route" "compute_route" {
  provider = google-beta

  name = "compute-route"
  description = "A sample compute route"
  network = "projects/tjr-dm-test-1/global/networks/compute-network"
  tags = [
    "tag1"
  ]
  dest_range = "0.0.0.0/0"
  priority = 100
  next_hop_ip = "10.2.0.4"

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_disk.compute_disk  __project__/us-west1-c/compute-disk
resource "google_compute_disk" "compute_disk" {
  provider = google-beta

  name = "compute-disk"
  description = "a sample encrypted, blank disk"
  size = 1
  zone = "us-west1-c"
  physical_block_size_bytes = 4096
  disk_encryption_key {
    raw_key = "SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0="
  }
  type = "pd-ssd"
}
