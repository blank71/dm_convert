provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_disk.compute_disk_1  __project__/us-west1-a/compute-disk-1
resource "google_compute_disk" "compute_disk_1" {
  provider = google-beta

  name = "compute-disk-1"
  description = "a sample encrypted, blank disk"
  size = 1
  zone = "us-west1-a"
  physical_block_size_bytes = 4096
  disk_encryption_key {
    raw_key = "SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0="
  }
  type = "pd-ssd"
}

#tfimport-terraform import google_compute_disk.compute_disk_2  __project__/us-west1-a/compute-disk-2
resource "google_compute_disk" "compute_disk_2" {
  provider = google-beta

  name = "compute-disk-2"
  size = 1
  zone = "us-west1-a"
  type = "pd-ssd"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork __project__/us-west1/compute-subnetwork
resource "google_compute_subnetwork" "compute_subnetwork" {
  provider = google-beta

  name = "compute-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region = "us-west1"
  network = google_compute_network.compute_network.id
  secondary_ip_range {
    ip_cidr_range = "10.3.16.0/20"
    range_name = "cloudrange"
  }

  depends_on = [
    google_compute_network.compute_network
  ]
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.disks.diskEncryptionKey.rawKey: ['SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0=']
#
#tfimport-terraform import google_compute_instance.compute_instance  __project__/us-west1-a/compute-instance
resource "google_compute_instance" "compute_instance" {
  provider = google-beta

  name = "compute-instance"
  can_ip_forward = false
  min_cpu_platform = "Intel Skylake"
  zone = "us-west1-a"
  machine_type = "n1-standard-1"
  labels = {
    created-from = "image"
    network-type = "subnetwork"
  }
  boot_disk {
    auto_delete = false
    initialize_params {
      size = 24
      image = "projects/debian-cloud/global/images/family/debian-11"
      type = "pd-ssd"
    }
  }
  attached_disk {
    device_name = "proxycontroldisk"
    mode = "READ_ONLY"
    disk_encryption_key_raw = "SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0="
    source = google_compute_disk.compute_disk_1.id
  }
  attached_disk {
    device_name = "persistentdisk"
    mode = "READ_WRITE"
    source = google_compute_disk.compute_disk_2.id
  }
  network_interface {
    subnetwork = "projects/tjr-dm-test-1/regions/us-west1/subnetworks/compute-subnetwork"
    alias_ip_range {
      ip_cidr_range = "/24"
      subnetwork_range_name = "cloudrange"
    }
  }
  service_account {
    email = "cnrm-system@tjr-dm-test-1.iam.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/compute", "https://www.googleapis.com/auth/logging.write"]
  }

  depends_on = [
    google_compute_disk.compute_disk_1,
    google_compute_disk.compute_disk_2,
    google_compute_subnetwork.compute_subnetwork
  ]
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.disks.diskEncryptionKey.rawKey: ['SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0=']
#
#tfimport-terraform import google_compute_instance.compute_beta_instance  __project__/us-west1-a/compute-beta-instance
resource "google_compute_instance" "compute_beta_instance" {
  provider = google-beta

  name = "compute-beta-instance"
  can_ip_forward = false
  min_cpu_platform = "Intel Skylake"
  zone = "us-west1-a"
  machine_type = "n1-standard-1"
  labels = {
    created-from = "image"
    network-type = "subnetwork"
  }
  boot_disk {
    auto_delete = false
    initialize_params {
      size = 24
      image = "projects/debian-cloud/global/images/family/debian-11"
      type = "pd-ssd"
    }
  }
  attached_disk {
    device_name = "proxycontroldisk"
    mode = "READ_ONLY"
    disk_encryption_key_raw = "SGVsbG8gZnJvbSBHb29nbGUgQ2xvdWQgUGxhdGZvcm0="
    source = google_compute_disk.compute_disk_1.id
  }
  attached_disk {
    device_name = "persistentdisk"
    mode = "READ_WRITE"
    source = google_compute_disk.compute_disk_2.id
  }
  network_interface {
    subnetwork = "projects/tjr-dm-test-1/regions/us-west1/subnetworks/compute-subnetwork"
    alias_ip_range {
      ip_cidr_range = "/24"
      subnetwork_range_name = "cloudrange"
    }
  }
  service_account {
    email = "cnrm-system@tjr-dm-test-1.iam.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/compute", "https://www.googleapis.com/auth/logging.write"]
  }

  depends_on = [
    google_compute_disk.compute_disk_1,
    google_compute_disk.compute_disk_2,
    google_compute_subnetwork.compute_subnetwork
  ]
}
