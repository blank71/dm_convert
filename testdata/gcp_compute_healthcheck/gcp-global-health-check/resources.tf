provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_health_check.compute_healthcheck  __project__/compute-healthcheck
resource "google_compute_health_check" "compute_healthcheck" {
  provider = google-beta

  name = "compute-healthcheck"
  check_interval_sec = 10
  http_health_check {
    port = 80
  }
}
