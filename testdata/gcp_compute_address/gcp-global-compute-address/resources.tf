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

resource "google_compute_global_address" "compute_globaladdress" {
  provider = google-beta

  name = "compute-globaladdress"
  description = "a test global address"
  ip_version = "IPV4"
  prefix_length = 16
  address_type = "INTERNAL"
  purpose = "VPC_PEERING"
  network = google_compute_network.compute_network.id

  depends_on = [
    google_compute_network.compute_network
  ]
}
#tfimport-terraform import google_compute_global_address.compute_globaladdress  projects/__project__/global/addresses/compute-globaladdress
