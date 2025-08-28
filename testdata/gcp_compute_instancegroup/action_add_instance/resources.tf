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
    raw_key = "SGVsbG8gZnJvbSBHb29nbGUgAAxvdWQgUGxhdGZvcm0="
  }
  type = "pd-ssd"
}

#tfimport-terraform import google_compute_disk.compute_disk_2  __project__/us-west1-a/compute-disk-2
resource "google_compute_disk" "compute_disk_2" {
  provider = google-beta

  name = "compute-disk-2"
  description = "a sample encrypted, blank disk-2"
  size = 1
  zone = "us-west1-a"
  physical_block_size_bytes = 4096
  disk_encryption_key {
    raw_key = "SGVsbG8gZnJvbSBHb29nbGUgAAxvdWQgUGxhdGZ1110="
  }
  type = "pd-ssd"
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.disks.diskEncryptionKey.rawKey: ['SGVsbG8gZnJvbSBHb29nbGUgAAxvdWQgUGxhdGZvcm0=']
#
#tfimport-terraform import google_compute_instance.vm_1  __project__/us-central1-a/vm-1
resource "google_compute_instance" "vm_1" {
  provider = google-beta

  name = "vm-1"
  zone = "us-central1-a"
  machine_type = "n1-standard-1"
  boot_disk {
    device_name = "boot"
    mode = "READ_ONLY"
    disk_encryption_key_raw = "SGVsbG8gZnJvbSBHb29nbGUgAAxvdWQgUGxhdGZvcm0="
    source = google_compute_disk.compute_disk_1.id
  }
  network_interface {
    network = "global/networks/default"
  }

  depends_on = [
    google_compute_disk.compute_disk_1
  ]
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.disks.diskEncryptionKey.rawKey: ['SGVsbG8gZnJvbSBHb29nbGUgAAxvdWQgUGxhdGZ1110=']
#
#tfimport-terraform import google_compute_instance.vm_2  __project__/us-central1-a/vm-2
resource "google_compute_instance" "vm_2" {
  provider = google-beta

  name = "vm-2"
  zone = "us-central1-a"
  machine_type = "n1-standard-1"
  boot_disk {
    device_name = "boot"
    mode = "READ_ONLY"
    disk_encryption_key_raw = "SGVsbG8gZnJvbSBHb29nbGUgAAxvdWQgUGxhdGZ1110="
    source = google_compute_disk.compute_disk_2.id
  }
  network_interface {
    network = "global/networks/default"
  }

  depends_on = [
    google_compute_disk.compute_disk_2
  ]
}

#tfimport-terraform import google_compute_instance_group.instancegroup  __project__/us-central1-f/instancegroup
resource "google_compute_instance_group" "instancegroup" {
  provider = google-beta

  name = "instancegroup"
  zone = "us-central1-f"
  instances = [
    google_compute_instance.vm_1.id,
    google_compute_instance.vm_2.id
  ]

  depends_on = [
    google_compute_disk.compute_disk_1,
    google_compute_disk.compute_disk_2,
    google_compute_instance.vm_1,
    google_compute_instance.vm_2
  ]
}
