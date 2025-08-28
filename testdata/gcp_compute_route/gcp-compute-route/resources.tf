provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  description = "Default network for the project"
  auto_create_subnetworks = true
}

#tfimport-terraform import google_compute_route.compute_route  __project__/compute-route
resource "google_compute_route" "compute_route" {
  provider = google-beta

  name = "compute-route"
  description = "A sample compute route"
  network = google_compute_network.compute_network.id
  tags = [
    "tag1",
    "tag2"
  ]
  dest_range = "0.0.0.0/0"
  priority = 100
  next_hop_ip = "10.132.0.5"

  depends_on = [
    google_compute_network.compute_network
  ]
}
