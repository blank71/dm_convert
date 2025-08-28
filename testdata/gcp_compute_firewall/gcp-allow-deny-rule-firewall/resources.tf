provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
}

#tfimport-terraform import google_compute_firewall.compute_firewall_1  __project__/compute-firewall-1
resource "google_compute_firewall" "compute_firewall_1" {
  provider = google-beta

  name = "compute-firewall-1"
  description = "abc"
  disabled = false
  direction = "EGRESS"
  destination_ranges = [
    "192.168.0.0/16"
  ]
  network = google_compute_network.compute_network.id
  deny {
    protocol = "tcp"
    ports = ["80"]
  }

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_firewall.compute_firewall_2  __project__/compute-firewall-2
resource "google_compute_firewall" "compute_firewall_2" {
  provider = google-beta

  name = "compute-firewall-2"
  description = "abc"
  disabled = false
  direction = "INGRESS"
  priority = 999
  source_ranges = [
    "192.168.0.0/16"
  ]
  source_service_accounts = [
    "test1@google.com",
    "test2@google.com"
  ]
  target_service_accounts = [
    "test3@google.com",
    "test4@google.com"
  ]
  log_config {
    metadata = "EXCLUDE_ALL_METADATA"
  }
  network = google_compute_network.compute_network.id
  allow {
    protocol = "tcp"
    ports = ["11234", "16180"]
  }

  depends_on = [
    google_compute_network.compute_network
  ]
}
