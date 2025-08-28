provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_dns_managed_zone.dns_managed_zone __project__/dns-managed-zone
resource "google_dns_managed_zone" "dns_managed_zone" {
  provider = google-beta

  name = "dns-managed-zone"
  dns_name = "secure.tjr-dm-test-1-dns.com."
  description = "A sample managed zone."
  dnssec_config {
    state = "on"
  }

  force_destroy = false
}

#tfimport-terraform import google_dns_record_set.dns_record_set_1 __project__/dns-managed-zone/dns_record_set_1/DS
resource "google_dns_record_set" "dns_record_set_1" {
  provider = google-beta

  name = "dns_record_set_1."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  type = "DS"
  ttl = 300
  rrdatas = [
    "31523 5 1 c8761ba5defc26ac7b78e076d7c47fa9f86b9fba"
  ]

  depends_on = [
    google_dns_managed_zone.dns_managed_zone
  ]
}
