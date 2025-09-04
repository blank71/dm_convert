provider "google-beta" {
  project = "None"
}

resource "google_compute_region_disk" "compute_regiondisk" {
  provider = google-beta

  name = "compute-regiondisk"
  region = "us-west1"
  replica_zones = [
    "zones/us-west1-a",
    "zones/us-west1-b"
  ]
  description = "A 600GB regional disk."
  size = 600
  physical_block_size_bytes = 16384
  labels = {
    extra-gb = "100"
  }
}
#tfimport-terraform import google_compute_region_disk.compute_regiondisk  projects/__project__/regions/us-west1/disks/compute-regiondisk
