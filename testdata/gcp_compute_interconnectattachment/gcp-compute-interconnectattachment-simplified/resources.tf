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

#tfimport-terraform import google_compute_router.compute_router  __project__//router-sample
resource "google_compute_router" "compute_router" {
  provider = google-beta

  name = "router-sample"
  network = google_compute_network.compute_network.id
  bgp {
    asn = 16550
  }

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_interconnect_attachment.compute_interconnect_attachment  __project__//interconnect-sample
resource "google_compute_interconnect_attachment" "compute_interconnect_attachment" {
  provider = google-beta

  description = "sample configuration"
  name = "interconnect-sample"
  router = google_compute_router.compute_router.id
  mtu = 1500
  type = "PARTNER"
  vlan_tag8021q = 1024
  edge_availability_domain = "AVAILABILITY_DOMAIN_1"
  candidate_subnets = [
    "169.254.0.0/16",
    "192.0.0.0/16"
  ]
  encryption = "IPSEC"
}
