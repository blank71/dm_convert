provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_container_cluster.resource_container_cluster __project__/us-central1-a/resource-container-cluster
resource "google_container_cluster" "resource_container_cluster" {
  provider = google-beta

  name = "resource-container-cluster"
  description = "this is descriptoin for testing"
  logging_service = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"
  network = "container-cluster-network"
  subnetwork = "container-cluster-subnetwork"
  node_locations = [
    "us-central1",
    "us-central2"
  ]
  enable_kubernetes_alpha = false
  min_master_version = 123
  enable_tpu = false
  initial_node_count = 1
  location = "us-central1-a"
  enable_legacy_abac = false
  binary_authorization {
    enabled = false
  }
  default_max_pods_per_node = 4
  enable_shielded_nodes = false
  node_config {
    machine_type = "n1-standard-1"
    disk_size_gb = 100
    oauth_scopes = [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/trace.append"
    ]
    service_account = "1234-compute@developer.gserviceaccount.com"
    local_ssd_count = 2
    tags = [
      "tag1",
      "tag2",
      "tag3"
    ]
    preemptible = true
    disk_type = "pd-balanced"
    min_cpu_platform = "Intel Haswell"
    guest_accelerator {
      count = 1
      type = "nvidia-tesla-k80"
    }
    guest_accelerator {
      count = 1
      type = "a2-highgpu-1g"
    }
    shielded_instance_config {
      enable_secure_boot = false
      enable_integrity_monitoring = true
    }
    taint {
      effect = "NO_SCHEDULE"
      key = "taints-key1"
      value = "taints-value1"
    }
    taint {
      effect = "NO_EXECUTE"
      key = "taints-key2"
      value = "taints-value2"
    }
    workload_metadata_config {
      mode = "GCE_METADATA"
    }
    metadata = {
      "metadata-field-1" = "metadata-value-1"
      "metadata-field-2" = "metadata-value-2"
    }
    labels = {
      label-one = "value-one"
      label-two = "value-two"
    }
  }
  default_snat_status {
    disabled = false
  }
  datapath_provider = "LEGACY_DATAPATH"
  private_ipv6_google_access = "PRIVATE_IPV6_GOOGLE_ACCESS_TO_GOOGLE"
  enable_intranode_visibility = false
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
    cloudrun_config {
      disabled = false
      load_balancer_type = "LOAD_BALANCER_TYPE_INTERNAL"
    }
  }
  resource_labels = {
    "resource-label-one" = "resource-value-one"
    "resource-label-two" = "resource-value-two"
  }
  network_policy {
    provider = "CALICO"
    enabled = false
  }
  ip_allocation_policy {
    cluster_ipv4_cidr_block = "10.96.0.0/14"
    services_ipv4_cidr_block = "172.16.0.0/12"
  }
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block = "10.0.0.0/8"
      display_name = "cidr_block_1"
    }
    cidr_blocks {
      cidr_block = "10.0.0.0/28"
      display_name = "cidr_block_2"
    }
  }
  maintenance_policy {
    daily_maintenance_window {
      start_time = "15:01"
    }
    maintenance_exclusion {
      exclusion_name = "maintenance-exclusion-1"
      start_time = "2014-10-02T15:01:23Z"
      end_time = "2014-10-02T15:01:23.045123456Z"
    }
    maintenance_exclusion {
      exclusion_name = "maintenance-exclusion-2"
      start_time = "2014-10-02T15:01:23Z"
      end_time = "2014-10-02T15:01:23.045123456Z"
    }
  }
  cluster_autoscaling {
    enabled = false
    resource_limits {
      maximum = 2000
      minimum = 1000
      resource_type = "cpu"
    }
    resource_limits {
      maximum = 32
      minimum = 16
      resource_type = "ram"
    }
  }
  resource_usage_export_config {
    enable_network_egress_metering = false
    bigquery_destination {
      dataset_id = "resourceUsageExportConfig-bq-dataset-id"
    }
    enable_resource_consumption_metering = false
  }
  authenticator_groups_config {
    security_group = "authenticator-security-group"
  }
  private_cluster_config {
    enable_private_nodes = false
    enable_private_endpoint = false
    master_ipv4_cidr_block = "10.0.0.0/28"
    master_global_access_config {
      enabled = false
    }
  }
  database_encryption {
    state = "ENCRYPTED"
    key_name = "db-encryption-key-name"
  }
  vertical_pod_autoscaling {
    enabled = false
  }
  release_channel {
    channel = "REGULAR"
  }
}
