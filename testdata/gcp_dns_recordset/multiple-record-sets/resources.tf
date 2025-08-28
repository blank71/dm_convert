provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_dns_managed_zone.dns_managed_zone __project__/dns-managed-zone
resource "google_dns_managed_zone" "dns_managed_zone" {
  provider = google-beta

  name = "dns-managed-zone"
  dns_name = "tjr-dm-test-1-dns.com."
  description = "A sample managed zone."

  force_destroy = false
}

#tfimport-terraform import google_dns_record_set.dns_record_set_1 __project__/dns-managed-zone/dns_record_set_1/CNAME
resource "google_dns_record_set" "dns_record_set_1" {
  provider = google-beta

  name = "dns_record_set_1."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  type = "CNAME"
  ttl = 300
  rrdatas = [
    "www.tjr-dm-test-1-dns.com."
  ]

  depends_on = [
    google_dns_managed_zone.dns_managed_zone
  ]
}

#tfimport-terraform import google_dns_record_set.dns_record_set_2 __project__/dns-managed-zone/dns_record_set_2/AAAA
resource "google_dns_record_set" "dns_record_set_2" {
  provider = google-beta

  name = "dns_record_set_2."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  type = "AAAA"
  ttl = 300
  rrdatas = [
    "8888:8888:8888:8888::"
  ]

  depends_on = [
    google_dns_managed_zone.dns_managed_zone
  ]
}

#tfimport-terraform import google_dns_record_set.dns_record_set_3 __project__/dns-managed-zone/dns_record_set_3/MX
resource "google_dns_record_set" "dns_record_set_3" {
  provider = google-beta

  name = "dns_record_set_3."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  type = "MX"
  ttl = 300
  rrdatas = [
    "5 gmr-stmp-in.l.google.com.",
    "10 alt1.gmr-stmp-in.l.google.com.",
    "10 alt2.gmr-stmp-in.l.google.com.",
    "10 alt3.gmr-stmp-in.l.google.com.",
    "10 alt4.gmr-stmp-in.l.google.com."
  ]

  depends_on = [
    google_dns_managed_zone.dns_managed_zone
  ]
}

#tfimport-terraform import google_dns_record_set.dns_record_set_4 __project__/dns-managed-zone/dns_record_set_4/A
resource "google_dns_record_set" "dns_record_set_4" {
  provider = google-beta

  name = "dns_record_set_4."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  type = "A"
  ttl = 300
  rrdatas = [
    "8.8.8.8"
  ]

  depends_on = [
    google_dns_managed_zone.dns_managed_zone
  ]
}

#tfimport-terraform import google_dns_record_set.dns_record_set_5 __project__/dns-managed-zone/dns_record_set_5/TXT
resource "google_dns_record_set" "dns_record_set_5" {
  provider = google-beta

  name = "dns_record_set_5."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  type = "TXT"
  ttl = 300
  rrdatas = [
    "\"This is a sample DNS text record string\"",
    "Text records are normally split on spaces",
    "To prevent this, \"quote your text like this\""
  ]

  depends_on = [
    google_dns_managed_zone.dns_managed_zone
  ]
}

#tfimport-terraform import google_dns_record_set.dns_record_set_6 __project__/dns-managed-zone/dns_record_set_6/SRV
resource "google_dns_record_set" "dns_record_set_6" {
  provider = google-beta

  name = "dns_record_set_6."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  type = "SRV"
  ttl = 300
  rrdatas = [
    "0 0 9 tcpserver.cnrm-dns-tjr-dm-test-1-dns.com."
  ]

  depends_on = [
    google_dns_managed_zone.dns_managed_zone
  ]
}
