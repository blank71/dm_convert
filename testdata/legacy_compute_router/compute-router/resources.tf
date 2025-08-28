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

#tfimport-terraform import google_compute_router.compute_router  __project__/us-west1/compute-router
resource "google_compute_router" "compute_router" {
  provider = google-beta

  name = "compute-router"
  description = "example router description"
  network = "projects/tjr-dm-test-1/global/networks/compute-network"
  region = "us-west1"
  bgp {
    asn = 64514
    advertise_mode = "CUSTOM"
    advertised_groups = [
      "ALL_SUBNETS"
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

#tfimport-terraform import google_compute_router.compute_routers  __project__/us-west1/compute-routers
resource "google_compute_router" "compute_routers" {
  provider = google-beta

  name = "compute-routers"
  description = "example router description"
  network = "projects/tjr-dm-test-1/global/networks/compute-network"
  region = "us-west1"
  bgp {
    asn = 64514
    advertise_mode = "CUSTOM"
    advertised_groups = [
      "ALL_SUBNETS"
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
