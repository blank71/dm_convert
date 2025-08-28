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

#tfimport-terraform import google_dns_record_set.gcp_dns_bucket_insert_action_test_1 my-test-project/dns-managed-zone/gcp_dns_bucket_insert_action_test_1/DNSKEY
resource "google_dns_record_set" "gcp_dns_bucket_insert_action_test_1" {
  provider = google-beta

  name = "gcp_dns_bucket_insert_action_test_1."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  project = "my-test-project"
  type = "DNSKEY"
  rrdatas = [
    "257 3 RSASHA256 AwEAAZkgE48ZLQtCZ0v8/qWGiXGn5CIvdWG6NWCG0LEb69RBpkfDztOQN5/i4T+GLXiwcEklZiFns/gf0D6aL8mpmSwl5ATOl+K4V1nXtreEX8kbhQoJsc6qkCBZGgoThm05bVlnSFjVhTM/WYVkk2u+vGD/3WkCpR4a6Xw+WzfHRrN8Qu1EUx9PqDCY6Tfhis4KQsydPFp6iOsR84scDjfrxLuJSQr0c2Sl+1eufqS9o0fr+azRXkelfvAOm2YAm/STj7JjM6bdIGTkeJxfGsGJRY7mOkNB8C3Q9OYyOyFJ2MHWwKvKs3LCj+Z3uinzmOplLDcgszCUPWNSYaCxAV2gguk=",
    "256 3 RSASHA256 AwEAAc1bLrrinMGU8Y9JnwFwunnhZylXyLgUuNY5rLqjvg89b5tdU9KEYNwUyAZVVmZq5pPVjKV+7jOx+ZhMGDrTMpQwzCm1VAHQuED5cNw4FFhXXe4E9VuPIWV0Yv1mtm6bt7GRtgZ8luqCmL8RQ+JlH3rFGawCst72h1MdTzaKoDDJ"
  ]
}

#tfimport-terraform import google_dns_record_set.gcp_dns_bucket_insert_action_test_2 my-test-project/dns-managed-zone/gcp_dns_bucket_insert_action_test_2/DNSKEY
resource "google_dns_record_set" "gcp_dns_bucket_insert_action_test_2" {
  provider = google-beta

  name = "gcp_dns_bucket_insert_action_test_2."
  managed_zone = google_dns_managed_zone.dns_managed_zone.name
  project = "my-test-project"
  type = "DNSKEY"
  ttl = 30
  rrdatas = [
    "5 gmr-stmp-in.l.google.com.",
    "10 alt1.gmr-stmp-in.l.google.com.",
    "10 alt2.gmr-stmp-in.l.google.com.",
    "10 alt3.gmr-stmp-in.l.google.com.",
    "10 alt4.gmr-stmp-in.l.google.com."
  ]

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }

  depends_on = [
    google_dns_managed_zone.dns_managed_zone
  ]
}
