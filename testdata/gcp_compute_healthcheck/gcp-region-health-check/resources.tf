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

#tfimport-terraform import google_compute_region_health_check.compute_healthcheck_ssl  my-test-ssl-dm-project/europe-west2/compute-healthcheck-ssl
resource "google_compute_region_health_check" "compute_healthcheck_ssl" {
  provider = google-beta

  name = "compute-healthcheck-ssl"
  check_interval_sec = 10
  project = "my-test-ssl-dm-project"
  ssl_health_check {
    port = 443
    port_name = "ssl"
  }
  region = "europe-west2"
}

#tfimport-terraform import google_compute_region_health_check.compute_healthcheck_http  my-test-http-dm-project/asia-south1/compute-healthcheck-http
resource "google_compute_region_health_check" "compute_healthcheck_http" {
  provider = google-beta

  name = "compute-healthcheck-http"
  check_interval_sec = 10
  project = "my-test-http-dm-project"
  http_health_check {
    port = 80
    port_name = "http"
  }
  region = "asia-south1"
}

#tfimport-terraform import google_compute_region_health_check.compute_healthcheck_https  my-test-https-dm-project/us-central1/compute-healthcheck-https
resource "google_compute_region_health_check" "compute_healthcheck_https" {
  provider = google-beta

  name = "compute-healthcheck-https"
  check_interval_sec = 10
  project = "my-test-https-dm-project"
  https_health_check {
    port = 8080
    port_name = "https"
  }
  region = "us-central1"
}

#tfimport-terraform import google_compute_region_health_check.compute_healthcheck_http2  my-test-http2-dm-project/europe-north1/compute-healthcheck-http2
resource "google_compute_region_health_check" "compute_healthcheck_http2" {
  provider = google-beta

  name = "compute-healthcheck-http2"
  check_interval_sec = 10
  project = "my-test-http2-dm-project"
  http2_health_check {
    port = 8081
    port_name = "http2"
  }
  region = "europe-north1"
}

#tfimport-terraform import google_compute_region_health_check.compute_healthcheck_grcp  my-test-grcp-dm-project/asia-east1/compute-healthcheck-grcp
resource "google_compute_region_health_check" "compute_healthcheck_grcp" {
  provider = google-beta

  name = "compute-healthcheck-grcp"
  check_interval_sec = 10
  project = "my-test-grcp-dm-project"
  grpc_health_check {
    port = 12345
    port_name = "grcp"
    grpc_service_name = "hello-world"
  }
  region = "asia-east1"
}
