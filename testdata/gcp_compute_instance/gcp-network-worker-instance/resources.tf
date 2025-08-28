provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}

#tfimport-terraform import google_compute_disk.compute_disk  __project__/us-west1-a/compute-disk
resource "google_compute_disk" "compute_disk" {
  provider = google-beta

  name = "compute-disk"
  description = "a sample encrypted, blank disk"
  size = 1
  zone = "us-west1-a"
  physical_block_size_bytes = 4096
  disk_encryption_key {
    raw_key = "SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0="
  }
  type = "pd-ssd"
}

#tfimport-terraform import google_compute_address.compute_address  __project__/us-west1/compute-address
resource "google_compute_address" "compute_address" {
  provider = google-beta

  name = "compute-address"
  description = "a sample external address"
  region = "us-west1"
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork __project__/us-west1/compute-subnetwork
resource "google_compute_subnetwork" "compute_subnetwork" {
  provider = google-beta

  name = "compute-subnetwork"
  description = "a sample subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region = "us-west1"
  private_ip_google_access = false
  network = google_compute_network.compute_network.id
    log_config {
      aggregation_interval = "INTERVAL_10_MIN"
      flow_sampling = 0.5
      metadata = "INCLUDE_ALL_METADATA"
      filter_expr = "true"
    }

  depends_on = [
    google_compute_network.compute_network
  ]
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.networkInterfaces.accessConfigs.type: ['ONE_TO_ONE_NAT']
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
  scratch_disk {
    interface = "SCSI"
  }
  scratch_disk {
    interface = "NVME"
  }
  network_interface {
    network_ip = "10.2.0.4"
    network = google_compute_network.compute_network.id
    subnetwork = google_compute_subnetwork.compute_subnetwork.id
    access_config {
      nat_ip = google_compute_address.compute_address.address
    }
  }
  scheduling {
    automatic_restart = false
    on_host_maintenance = "TERMINATE"
    preemptible = true
  }
  guest_accelerator {
    count = "1"
    type = "nvidia-tesla-v100"
  }

  depends_on = [
    google_compute_address.compute_address,
    google_compute_disk.compute_disk,
    google_compute_network.compute_network,
    google_compute_subnetwork.compute_subnetwork
  ]
}
