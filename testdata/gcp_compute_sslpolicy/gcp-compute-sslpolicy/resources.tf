provider "google-beta" {
  project = "None"
}

resource "google_compute_ssl_policy" "compute_sslpolicy" {
  provider = google-beta

  name = "compute-sslpolicy"
  min_tls_version = "TLS_1_2"
  profile = "COMPATIBLE"
}
#tfimport-terraform import google_compute_ssl_policy.compute_sslpolicy  projects/__project__/global/sslPolicies/compute-sslpolicy
