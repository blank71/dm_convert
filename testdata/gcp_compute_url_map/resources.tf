provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_http_health_check.health_check_test_deployment  __project__/health-check-test-deployment
resource "google_compute_http_health_check" "health_check_test_deployment" {
  provider = google-beta

  name = "health-check-test-deployment"
  check_interval_sec = 3
  description = "integration test http health check"
  healthy_threshold = 2
  host = "localhost"
  port = 8080
  request_path = "/path/to/my/service"
  timeout_sec = 3
  unhealthy_threshold = 5
}

#tfimport-terraform import google_compute_backend_service.bs1_test_deployment  __project__/bs1-test-deployment
resource "google_compute_backend_service" "bs1_test_deployment" {
  provider = google-beta

  name = "bs1-test-deployment"
  description = "backend service for integration tests"
  timeout_sec = 30
  protocol = "HTTP"
  port_name = "http"
  health_checks = [
  google_compute_http_health_check.health_check_test_deployment.id
  ]
}

#tfimport-terraform import google_compute_backend_service.bs2_test_deployment  __project__/bs2-test-deployment
resource "google_compute_backend_service" "bs2_test_deployment" {
  provider = google-beta

  name = "bs2-test-deployment"
  description = "backend service for integration tests"
  timeout_sec = 30
  protocol = "HTTP"
  port_name = "http"
  health_checks = [
  google_compute_http_health_check.health_check_test_deployment.id
  ]
}

#tfimport-terraform import google_compute_url_map.url_map_test_deployment_1  __project__/url-map-test-deployment-1
resource "google_compute_url_map" "url_map_test_deployment_1" {
  provider = google-beta

  name = "url-map-test-deployment-1"
  default_service = google_compute_backend_service.bs2_test_deployment.id
  host_rule{
    description = "test host rule"
    path_matcher = "url-set-1-test-deployment"
    hosts = [
    "*"
    ]
  }
  path_matcher{
    description = ""
    name = "url-set-1-test-deployment"
    default_service = google_compute_backend_service.bs1_test_deployment.id
  }
}

#tfimport-terraform import google_compute_url_map.url_map_test_deployment_2  __project__/url-map-test-deployment-2
resource "google_compute_url_map" "url_map_test_deployment_2" {
  provider = google-beta

  name = "url-map-test-deployment-2"
  default_service = google_compute_backend_service.bs2_test_deployment.id
  host_rule{
    description = "test host rule"
    path_matcher = "url-set-1-test-deployment"
    hosts = [
    "*"
    ]
  }
  path_matcher{
    description = ""
    name = "url-set-1-test-deployment"
    default_service = google_compute_backend_service.bs1_test_deployment.id
  }
}

#tfimport-terraform import google_compute_region_url_map.region_url_map_test_deployment_1  __project__/region-url-map-test-deployment-1
resource "google_compute_region_url_map" "region_url_map_test_deployment_1" {
  provider = google-beta

  name = "region-url-map-test-deployment-1"
  default_service = google_compute_backend_service.bs2_test_deployment.id
  host_rule{
    description = "test host rule"
    path_matcher = "url-set-1-test-deployment"
    hosts = [
    "*"
    ]
  }
  path_matcher{
    description = ""
    name = "url-set-1-test-deployment"
    default_service = google_compute_backend_service.bs1_test_deployment.id
  }
}
