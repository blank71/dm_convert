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

resource "google_compute_firewall" "compute_firewall" {
  provider = google-beta

  name = "compute-firewall"
  network = google_compute_network.compute_network.id
  allow {
    protocol = "tcp"
    ports = ["80", "1000-2000"]
  }

  depends_on = [
    google_compute_network.compute_network
  ]
}
#tfimport-terraform import google_compute_firewall.compute_firewall  projects/__project__/global/firewalls/compute-firewall
