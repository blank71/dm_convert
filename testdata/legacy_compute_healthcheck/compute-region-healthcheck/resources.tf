provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_region_health_check.compute_healthcheck_tcp  my-test-tcp-dm-project/us-west1/compute-healthcheck-tcp
resource "google_compute_region_health_check" "compute_healthcheck_tcp" {
  provider = google-beta

  name = "compute-healthcheck-tcp"
  check_interval_sec = 10
  project = "my-test-tcp-dm-project"
  tcp_health_check {
    port = 21
    port_name = "tcp"
  }
  region = "us-west1"
}
