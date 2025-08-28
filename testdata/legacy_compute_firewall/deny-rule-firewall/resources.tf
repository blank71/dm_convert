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

#tfimport-terraform import google_compute_firewall.compute_firewall  __project__/compute-firewall
resource "google_compute_firewall" "compute_firewall" {
  provider = google-beta

  name = "compute-firewall"
  network = google_compute_network.compute_network.id
  deny {
    protocol = "icmp"
  }

  depends_on = [
    google_compute_network.compute_network
  ]
}
