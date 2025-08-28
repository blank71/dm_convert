provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_container_cluster.container_cluster __project__/us-central1-a/container-cluster
resource "google_container_cluster" "container_cluster" {
  provider = google-beta

  name = "container-cluster"
  logging_service = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"
  initial_node_count = 1
  location = "us-central1-a"
  binary_authorization {
    evaluation_mode = "DISABLED"
  }
  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/trace.append"
    ]
  }
  default_snat_status {
    disabled = false
  }
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
  resource_labels = {
    "label-one" = "value-one"
  }
  cluster_autoscaling {
    enabled = false
  }
}
