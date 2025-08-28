provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
}

#tfimport-terraform import google_dns_managed_zone.dns_managedzone __project__/dns-managedzone
resource "google_dns_managed_zone" "dns_managedzone" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "dns-managedzone"
  dns_name = "tjr-dm-test-1-dns.com."
  description = "Example DNS zone"
  visibility = "private"
  private_visibility_config {
    networks {
      network_url = google_compute_network.compute_network.id
    }
  }

  force_destroy = false

  depends_on = [
    google_compute_network.compute_network
  ]
}
