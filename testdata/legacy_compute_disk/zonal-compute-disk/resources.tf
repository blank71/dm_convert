provider "google-beta" {
  project = "None"
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
