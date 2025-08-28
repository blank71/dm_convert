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

#tfimport-terraform import google_compute_backend_service.compute_backendservice  __project__/compute-backendservice
resource "google_compute_backend_service" "compute_backendservice" {
  provider = google-beta

  name = "compute-backendservice"
  health_checks = [
  google_compute_health_check.compute_healthcheck.id
  ]
}

#tfimport-terraform import google_compute_url_map.compute_urlmap  __project__/compute-urlmap
resource "google_compute_url_map" "compute_urlmap" {
  provider = google-beta

  name = "compute-urlmap"
  default_service = "projects/tjr-dm-test-1/global/backendServices/compute-backendservice"
}

#tfimport-terraform import google_compute_target_http_proxy.compute_targethttpproxy  __project__/compute-targethttpproxy
resource "google_compute_target_http_proxy" "compute_targethttpproxy" {
  provider = google-beta

  name = "compute-targethttpproxy"
  description = "A sample proxy"
  url_map = google_compute_url_map.compute_urlmap.id

  depends_on = [
    google_compute_url_map.compute_urlmap
  ]
}

#tfimport-terraform import google_compute_region_target_http_proxy.compute_regiontargethttpproxies  __project__/compute-regiontargethttpproxies
resource "google_compute_region_target_http_proxy" "compute_regiontargethttpproxies" {
  provider = google-beta

  name = "compute-regiontargethttpproxies"
  description = "A sample proxy"
  url_map = google_compute_url_map.compute_urlmap.id

  depends_on = [
    google_compute_url_map.compute_urlmap
  ]
}
