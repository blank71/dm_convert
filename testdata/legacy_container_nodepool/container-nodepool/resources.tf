provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_container_cluster.container_cluster __project__//container-cluster
resource "google_container_cluster" "container_cluster" {
  provider = google-beta

  name = "container-cluster"
  logging_service = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"
  location = ""
  binary_authorization {
    enabled = false
  }
  default_snat_status {
    disabled = false
  }
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
  node_pool {
    name = "container-nodepool"
    initial_node_count = 1
    node_config {
      disk_size_gb = 100
      oauth_scopes = [
        "https://www.googleapis.com/auth/logging.write",
        "https://www.googleapis.com/auth/monitoring"
      ]
      tags = [
        "tagone",
        "tagtwo"
      ]
      preemptible = false
      disk_type = "pd-standard"
      min_cpu_platform = "Intel Haswell"
      guest_accelerator {
        count = 1
        type = "nvidia-tesla-k80"
      }
      metadata = {
        "disable-legacy-endpoints" = "true"
      }
    }
    autoscaling {
      min_node_count = 1
      max_node_count = 3
    }
    management {
      auto_upgrade = true
      auto_repair = true
    }
  }
  cluster_autoscaling {
    enabled = false
  }
}
