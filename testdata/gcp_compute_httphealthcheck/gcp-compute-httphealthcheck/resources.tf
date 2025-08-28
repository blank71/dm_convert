provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_http_health_check.compute_httphealthcheck_1  __project__/compute-httphealthcheck-1
resource "google_compute_http_health_check" "compute_httphealthcheck_1" {
  provider = google-beta

  name = "compute-httphealthcheck-1"
  check_interval_sec = 10
  description = "example HTTP health check"
  healthy_threshold = 2
  port = 80
  request_path = "/"
  timeout_sec = 5
  unhealthy_threshold = 2
}

#tfimport-terraform import google_compute_http_health_check.compute_httphealthcheck_2  __project__/compute-httphealthcheck-2
resource "google_compute_http_health_check" "compute_httphealthcheck_2" {
  provider = google-beta

  name = "compute-httphealthcheck-2"
  check_interval_sec = 10
  description = "example HTTP health check"
  healthy_threshold = 2
  port = 80
  request_path = "/"
  timeout_sec = 5
  unhealthy_threshold = 2
}

#tfimport-terraform import google_compute_http_health_check.compute_httphealthcheck_3  __project__/compute-httphealthcheck-3
resource "google_compute_http_health_check" "compute_httphealthcheck_3" {
  provider = google-beta

  name = "compute-httphealthcheck-3"
  check_interval_sec = 10
  description = "example HTTP health check"
  healthy_threshold = 2
  port = 80
  request_path = "/"
  timeout_sec = 5
  unhealthy_threshold = 2
}
