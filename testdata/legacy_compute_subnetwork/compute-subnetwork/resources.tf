provider "google-beta" {
  project = "None"
}

resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}
#tfimport-terraform import google_compute_network.compute_network  projects/__project__/global/networks/compute-network

resource "google_compute_subnetwork" "compute_subnetwork" {
  provider = google-beta

  name = "compute-subnetwork"
  description = "My subnet"
  ip_cidr_range = "192.168.0.0/24"
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
#tfimport-terraform import google_compute_subnetwork.compute_subnetwork projects/__project__/regions/us-west1/subnetworks/compute-subnetwork

resource "google_compute_subnetwork" "compute_subnetworks" {
  provider = google-beta

  name = "compute-subnetworks"
  description = "My subnet"
  ip_cidr_range = "192.168.0.0/24"
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
#tfimport-terraform import google_compute_subnetwork.compute_subnetworks projects/__project__/regions/us-west1/subnetworks/compute-subnetworks
