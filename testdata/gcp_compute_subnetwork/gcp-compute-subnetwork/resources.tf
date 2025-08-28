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

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork __project__/us-west1/compute-subnetwork
resource "google_compute_subnetwork" "compute_subnetwork" {
  provider = google-beta

  name = "compute-subnetwork"
  description = "My subnet"
  ip_cidr_range = "192.168.0.0/24"
  region = "us-west1"
  private_ip_google_access = false
  network = google_compute_network.compute_network.id
    log_config {
      aggregation_interval = "INTERVAL_10_MIN"
      flow_sampling = 0.5
      metadata = "INCLUDE_ALL_METADATA"
      filter_expr = "true"
    }

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork_1 __project__/us-west1/compute-subnetwork-1
resource "google_compute_subnetwork" "compute_subnetwork_1" {
  provider = google-beta

  name = "compute-subnetwork-1"
  description = "My subnet"
  ip_cidr_range = "192.168.1.0/24"
  region = "us-west1"
  private_ip_google_access = false
  network = google_compute_network.compute_network.id
    log_config {
      aggregation_interval = "INTERVAL_10_MIN"
      flow_sampling = 0.5
      metadata = "CUSTOM_METADATA"
      filter_expr = "false"
      metadata_fields = [
        "src_instance",
        "dest_instance"
      ]
    }

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork_2 __project__/us-west1/compute-subnetwork-2
resource "google_compute_subnetwork" "compute_subnetwork_2" {
  provider = google-beta

  name = "compute-subnetwork-2"
  description = "My subnet"
  ip_cidr_range = "192.168.2.0/24"
  region = "us-west1"
  purpose = "REGIONAL_MANAGED_PROXY"
  role = "ACTIVE"
  network = google_compute_network.compute_network.id

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork_3 __project__/us-west1/compute-subnetwork-3
resource "google_compute_subnetwork" "compute_subnetwork_3" {
  provider = google-beta

  name = "compute-subnetwork-3"
  ip_cidr_range = "192.168.3.0/24"
  region = "us-west1"
  network = "default"
}

#tfimport-terraform import google_compute_network.compute_network_2  __project__/compute-network-2
resource "google_compute_network" "compute_network_2" {
  provider = google-beta

  name = "compute-network-2"
  auto_create_subnetworks = false
  enable_ula_internal_ipv6 = true
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork_4 __project__/us-central1/compute-subnetwork-4
resource "google_compute_subnetwork" "compute_subnetwork_4" {
  provider = google-beta

  name = "compute-subnetwork-4"
  ip_cidr_range = "10.10.10.0/24"
  region = "us-central1"
  private_ip_google_access = false
  ipv6_access_type = "INTERNAL"
  stack_type = "IPV4_IPV6"
  network = google_compute_network.compute_network_2.id
  secondary_ip_range {
    ip_cidr_range = "172.16.0.0/12"
    range_name = "my-secondary-range"
  }

  depends_on = [
    google_compute_network.compute_network_2
  ]
}
