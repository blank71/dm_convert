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
    state = "transfer"
  }

  force_destroy = false
}

#tfimport-terraform import google_dns_record_set.dns_record_set __project__/dns-managed-zone/dns_record_set/DNSKEY
resource "google_dns_record_set" "dns_record_set" {
  provider = google-beta

  name = "dns_record_set."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  type = "DNSKEY"
  ttl = 300
  rrdatas = [
    "257 3 RSASHA256 AwEAAZkgE48ZLQtCZ0v8/qWGiXGn5CIvdWG6NWCG0LEb69RBpkfDztOQN5/i4T+GLXiwcEklZiFns/gf0D6aL8mpmSwl5ATOl+K4V1nXtreEX8kbhQoJsc6qkCBZGgoThm05bVlnSFjVhTM/WYVkk2u+vGD/3WkCpR4a6Xw+WzfHRrN8Qu1EUx9PqDCY6Tfhis4KQsydPFp6iOsR84scDjfrxLuJSQr0c2Sl+1eufqS9o0fr+azRXkelfvAOm2YAm/STj7JjM6bdIGTkeJxfGsGJRY7mOkNB8C3Q9OYyOyFJ2MHWwKvKs3LCj+Z3uinzmOplLDcgszCUPWNSYaCxAV2gguk=",
    "256 3 RSASHA256 AwEAAc1bLrrinMGU8Y9JnwFwunnhZylXyLgUuNY5rLqjvg89b5tdU9KEYNwUyAZVVmZq5pPVjKV+7jOx+ZhMGDrTMpQwzCm1VAHQuED5cNw4FFhXXe4E9VuPIWV0Yv1mtm6bt7GRtgZ8luqCmL8RQ+JlH3rFGawCst72h1MdTzaKoDDJ"
  ]
}
