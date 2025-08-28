provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_address.compute_address  __project__/us-west1/compute-address
resource "google_compute_address" "compute_address" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "compute-address"
  description = "a test regional address"
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
  description = "a test target vpn gateway"
  region = "us-west1"
  network = google_compute_network.compute_network.id

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_forwarding_rule.compute_forwardingrule_1  __project__/us-west1/compute-forwardingrule-1
resource "google_compute_forwarding_rule" "compute_forwardingrule_1" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "compute-forwardingrule-1"
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

#tfimport-terraform import google_compute_forwarding_rule.compute_forwardingrule_2  __project__/us-west1/compute-forwardingrule-2
resource "google_compute_forwarding_rule" "compute_forwardingrule_2" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "compute-forwardingrule-2"
  ip_address = google_compute_address.compute_address.address
  ip_protocol = "UDP"
  description = "A regional forwarding rule"
  port_range = "500"
  region = "us-west1"
  target = google_compute_vpn_gateway.compute_targetvpngateway.id

  depends_on = [
    google_compute_vpn_gateway.compute_targetvpngateway,
    google_compute_address.compute_address
  ]
}

#tfimport-terraform import google_compute_forwarding_rule.compute_forwardingrule_3  __project__/us-west1/compute-forwardingrule-3
resource "google_compute_forwarding_rule" "compute_forwardingrule_3" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "compute-forwardingrule-3"
  ip_address = google_compute_address.compute_address.address
  ip_protocol = "UDP"
  description = "A regional forwarding rule"
  port_range = "4500"
  region = "us-west1"
  target = google_compute_vpn_gateway.compute_targetvpngateway.id

  depends_on = [
    google_compute_vpn_gateway.compute_targetvpngateway,
    google_compute_address.compute_address
  ]
}

#tfimport-terraform import google_compute_vpn_tunnel.compute_vpntunnel __project__/us-west1/compute-vpntunnel
resource "google_compute_vpn_tunnel" "compute_vpntunnel" {
  provider = google-beta

  labels = {
    foo = "bar"
  }
  name = "compute-vpntunnel"
  region = "us-west1"
  target_vpn_gateway = google_compute_vpn_gateway.compute_targetvpngateway.id
  peer_ip = "15.0.0.120"
  shared_secret = "a secret message"
  local_traffic_selector = [
    "192.168.0.0/16"
  ]

  depends_on = [
    google_compute_vpn_gateway.compute_targetvpngateway,
    google_compute_forwarding_rule.compute_forwardingrule_1,
    google_compute_forwarding_rule.compute_forwardingrule_2,
    google_compute_forwarding_rule.compute_forwardingrule_3
  ]
}
