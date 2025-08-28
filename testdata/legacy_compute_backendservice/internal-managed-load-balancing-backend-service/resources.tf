provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_health_check.compute_healthcheck  __project__/compute-healthcheck
resource "google_compute_health_check" "compute_healthcheck" {
  provider = google-beta

  name = "compute-healthcheck"
  http_health_check {
    port = 80
  }
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}

#tfimport-terraform import google_compute_instance_group.compute_instancegroup  __project__/us-west1-a/compute-instancegroup
resource "google_compute_instance_group" "compute_instancegroup" {
  provider = google-beta

  name = "compute-instancegroup"
  network = google_compute_network.compute_network.id
  zone = "us-west1-a"

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_region_backend_service.compute_regionbackendservice  __project__/us-west1/compute-regionbackendservice
resource "google_compute_region_backend_service" "compute_regionbackendservice" {
  provider = google-beta

  name = "compute-regionbackendservice"
  description = "Internal managed backend service with Maglev session affinity."
  timeout_sec = 86400
  protocol = "HTTP"
  region = "us-west1"
  session_affinity = "HEADER_FIELD"
  load_balancing_scheme = "INTERNAL_MANAGED"
  locality_lb_policy = "MAGLEV"
  connection_draining_timeout_sec = 10
  health_checks = [
  google_compute_health_check.compute_healthcheck.id
  ]
  backend {
    balancing_mode = "RATE"
    capacity_scaler = 0.9
    description = "An instance group serving this backend with 90% of its capacity, as calculated by requests per second."
    group = google_compute_instance_group.compute_instancegroup.id
    max_rate = 10000
  }
  consistent_hash {
    http_header_name = "Hash string"
    minimum_ring_size = 1024
  }
  circuit_breakers {
    max_connections = 1024
    max_requests_per_connection = 1
    max_pending_requests = 1024
    max_requests = 1024
    max_retries = 3
  }
  outlier_detection {
    consecutive_errors = 5
    interval {
      seconds = 9
      nanos = 999999999
    }
    base_ejection_time {
      seconds = 29
      nanos = 999999999
    }
    max_ejection_percent = 10
    enforcing_consecutive_errors = 100
    enforcing_success_rate = 100
    success_rate_minimum_hosts = 5
    success_rate_request_volume = 100
    success_rate_stdev_factor = 1900
    consecutive_gateway_failure = 5
  }
}

#tfimport-terraform import google_compute_region_backend_service.compute_regionbackendservices  __project__/us-west1/compute-regionbackendservices
resource "google_compute_region_backend_service" "compute_regionbackendservices" {
  provider = google-beta

  name = "compute-regionbackendservices"
  description = "Internal managed backend service with Maglev session affinity."
  timeout_sec = 86400
  protocol = "HTTP"
  region = "us-west1"
  session_affinity = "HEADER_FIELD"
  load_balancing_scheme = "INTERNAL_MANAGED"
  locality_lb_policy = "MAGLEV"
  connection_draining_timeout_sec = 10
  health_checks = [
  google_compute_health_check.compute_healthcheck.id
  ]
  backend {
    balancing_mode = "RATE"
    capacity_scaler = 0.9
    description = "An instance group serving this backend with 90% of its capacity, as calculated by requests per second."
    group = google_compute_instance_group.compute_instancegroup.id
    max_rate = 10000
  }
  consistent_hash {
    http_header_name = "Hash string"
    minimum_ring_size = 1024
  }
  circuit_breakers {
    max_connections = 1024
    max_requests_per_connection = 1
    max_pending_requests = 1024
    max_requests = 1024
    max_retries = 3
  }
  outlier_detection {
    consecutive_errors = 5
    interval {
      seconds = 9
      nanos = 999999999
    }
    base_ejection_time {
      seconds = 29
      nanos = 999999999
    }
    max_ejection_percent = 10
    enforcing_consecutive_errors = 100
    enforcing_success_rate = 100
    success_rate_minimum_hosts = 5
    success_rate_request_volume = 100
    success_rate_stdev_factor = 1900
    consecutive_gateway_failure = 5
  }
}
