provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
}

#tfimport-terraform import google_compute_vpn_gateway.compute_vpngateway __project__/us-central1/compute-vpngateway
resource "google_compute_vpn_gateway" "compute_vpngateway" {
  provider = google-beta

  name = "compute-vpngateway"
  description = "Compute VPN Gateway Sample"
  region = "us-central1"
  network = "projects/tjr-dm-test-1/global/networks/compute-network"

  depends_on = [
    google_compute_network.compute_network
  ]
}
