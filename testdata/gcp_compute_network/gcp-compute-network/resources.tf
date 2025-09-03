provider "google-beta" {
  project = "None"
}

resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = true
  routing_mode = "REGIONAL"
}
#tfimport-terraform import google_compute_network.compute_network  projects/__project__/global/networks/compute-network
