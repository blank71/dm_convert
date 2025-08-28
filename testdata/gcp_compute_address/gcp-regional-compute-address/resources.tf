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

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork __project__/us-west1/compute-subnetwork
resource "google_compute_subnetwork" "compute_subnetwork" {
  provider = google-beta

  name = "compute-subnetwork"
  ip_cidr_range = "10.10.10.0/24"
  region = "us-west1"
  private_ip_google_access = false
  network = google_compute_network.compute_network.id

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_address.compute_address  __project__/us-west1/compute-address
resource "google_compute_address" "compute_address" {
  provider = google-beta

  name = "compute-address"
  address_type = "INTERNAL"
  description = "a test regional address"
  region = "us-west1"
  ip_version = "IPV4"
  subnetwork = google_compute_subnetwork.compute_subnetwork.id

  depends_on = [
    google_compute_subnetwork.compute_subnetwork
  ]
}
