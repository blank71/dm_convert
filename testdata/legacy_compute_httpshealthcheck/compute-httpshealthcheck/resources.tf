provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_https_health_check.compute_httpshealthcheck  __project__/compute-httpshealthcheck
resource "google_compute_https_health_check" "compute_httpshealthcheck" {
  provider = google-beta

  name = "compute-httpshealthcheck"
  description = "example HTTPS health check"
  request_path = "/"
  port = 80
  check_interval_sec = 10
  timeout_sec = 5
  unhealthy_threshold = 2
  healthy_threshold = 2
}
