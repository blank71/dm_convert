provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_address.compute_address  __project__/us-west1/compute-address
resource "google_compute_address" "compute_address" {
  provider = google-beta

  name = "compute-address"
  region = "us-west1"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}

#tfimport-terraform import google_compute_vpn_gateway.compute_targetvpngateway __project__/us-west1/compute-targetvpngateway
resource "google_compute_vpn_gateway" "compute_targetvpngateway" {
  provider = google-beta

  name = "compute-targetvpngateway"
  description = "a regional target vpn gateway"
  region = "us-west1"
  network = google_compute_network.compute_network.id

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_forwarding_rule.compute_forwardingrule  __project__/us-west1/compute-forwardingrule
resource "google_compute_forwarding_rule" "compute_forwardingrule" {
  provider = google-beta

  name = "compute-forwardingrule"
  ip_address = google_compute_address.compute_address.address
  ip_protocol = "ESP"
  description = "A regional forwarding rule"
  region = "us-west1"
  target = google_compute_vpn_gateway.compute_targetvpngateway.id

  depends_on = [
    google_compute_vpn_gateway.compute_targetvpngateway,
    google_compute_address.compute_address
  ]
}
