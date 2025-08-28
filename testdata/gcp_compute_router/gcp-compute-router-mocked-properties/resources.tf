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

#tfimport-terraform import google_compute_router.compute_router  my-test-project/us-west1/compute-router
resource "google_compute_router" "compute_router" {
  provider = google-beta

  name = "compute-router"
  description = "a mocked config sample for testing only"
  network = google_compute_network.compute_network.id
  region = "us-west1"
  project = "my-test-project"
  bgp {
    asn = 64514
    advertise_mode = "CUSTOM"
    advertised_groups = [
      "ALL_SUBNETS",
      "ALL_VPC_SUBNETS"
    ]
    advertised_ip_ranges {
      description = ""
      range = "1.2.3.4"
    }
  }

  depends_on = [
    google_compute_network.compute_network
  ]
}
resource "google_compute_router_interface" "test_interface_1" {
  name = "test-interface-1"
  ip_range = "123.456.789.0"
  interconnect_attachment = "linkedInterconnectAttachment-prop-1"

  router = google_compute_router.compute_router.name
  region = "us-west1"
  project = "my-test-project"

  depends_on = [
    google_compute_router.compute_router
  ]
}
resource "google_compute_router_interface" "test_interface_2" {
  name = "test-interface-2"
  ip_range = "9.9.9.9"
  vpn_tunnel = "linkedVpnTunnel-prop-2"

  router = google_compute_router.compute_router.name
  region = "us-west1"
  project = "my-test-project"

  depends_on = [
    google_compute_router.compute_router
  ]
}
resource "google_compute_router_peer" "peer_2" {
  name = "peer-2"
  interface = "test-interface-1"
  peer_ip_address = "2.2.2.2"
  peer_asn = 20300
  advertised_route_priority = 1
  advertise_mode = "DEFAULT"
  advertised_groups = [
    "ALL_SUBNETS",
    "ALL_VPC_SUBNETS"
  ]

  router = google_compute_router.compute_router.name
  region = "us-west1"
  project = "my-test-project"

  depends_on = [
    google_compute_router.compute_router
  ]
}
resource "google_compute_router_nat" "nat_1" {
  name = "nat-1"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  nat_ips = [
    "10.10.10.1",
    "10.10.10.2"
  ]
  drain_nat_ips = [
    "10.10.20.1",
    "10.10.20.2"
  ]
  nat_ip_allocate_option = "AUTO_ONLY"
  min_ports_per_vm = 50
  udp_idle_timeout_sec = 100
  icmp_idle_timeout_sec = 200
  tcp_established_idle_timeout_sec = 300
  tcp_transitory_idle_timeout_sec = 400
  enable_endpoint_independent_mapping = false
  log_config {
    enable = false
    filter = "TRANSLATIONS_ONLY"
  }
  subnetwork {
    name = google_compute_network.compute_network.id
    secondary_ip_range_names = ["subnetwork-1", "subnetwork-2", "subnetwork-3"]
    source_ip_ranges_to_nat = ["PRIMARY_IP_RANGE", "LIST_OF_SECONDARY_IP_RANGES"]
  }
  subnetwork {
    name = "my_sub_net_1"
    secondary_ip_range_names = ["subnetwork-10", "subnetwork-20", "subnetwork-30"]
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }

  router = google_compute_router.compute_router.name
  region = "us-west1"
  project = "my-test-project"

  depends_on = [
    google_compute_router.compute_router
  ]
}
