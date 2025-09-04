provider "google-beta" {
  project = "None"
}

resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}
#tfimport-terraform import google_compute_network.compute_network  projects/__project__/global/networks/compute-network

resource "google_compute_router" "compute_router" {
  provider = google-beta

  name = "compute-router"
  description = "example router description"
  network = google_compute_network.compute_network.id
  region = "us-west1"
  project = "__project__"
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
#tfimport-terraform import google_compute_router.compute_router  projects/__project__/regions/us-west1/routers/compute-router
