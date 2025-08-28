provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_interconnect.example_interconnect  __project__//example-interconnect
resource "google_compute_interconnect" "example_interconnect" {
  provider = google-beta

  name = "example-interconnect"
  customer_name = "example_customer"
  interconnect_type = "DEDICATED"
  link_type = "LINK_TYPE_ETHERNET_10G_LR"
  location = "https://www.googleapis.com/compute/v1/projects/dm-convert-prow/global/interconnectLocations/iad-zone1-1"
  requested_link_count = 1
}
