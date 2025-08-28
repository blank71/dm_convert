provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_disk.compute_disk  __project__/us-west1-c/compute-disk
resource "google_compute_disk" "compute_disk" {
  provider = google-beta

  name = "compute-disk"
  description = "a sample encrypted, blank disk"
  size = 1
  zone = "us-west1-c"
  physical_block_size_bytes = 4096
  type = "pd-ssd"
}

#tfimport-terraform import google_compute_image.compute_image  __project__/compute-image
resource "google_compute_image" "compute_image" {
  provider = google-beta

  name = "compute-image"
  description = "A sample image created from an empty disk resource"
  raw_disk {
    container_type = "TAR"
    source = "test-source"
  }
  source_disk = google_compute_disk.compute_disk.id

  depends_on = [
    google_compute_disk.compute_disk
  ]
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork __project__/us-west1/compute-subnetwork
resource "google_compute_subnetwork" "compute_subnetwork" {
  provider = google-beta

  name = "compute-subnetwork"
  description = "a sample subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region = "us-west1"
  private_ip_google_access = false
  network = google_compute_network.compute_network.id
    log_config {
      aggregation_interval = "INTERVAL_10_MIN"
      flow_sampling = 0.5
      metadata = "INCLUDE_ALL_METADATA"
      filter_expr = "true"
    }

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_instance_template.compute_instancetemplate  __project__/compute-instancetemplate
resource "google_compute_instance_template" "compute_instancetemplate" {
  provider = google-beta

  description = "a sample instance template"
  instance_description = "a sample instance created from the sample instance template"
  tags = [
    "foo",
    "bar"
  ]
  machine_type = "n1-standard-1"
  min_cpu_platform = "Intel Skylake"
  labels = {
    env = "dev"
  }
  network_interface {
    network = google_compute_network.compute_network.id
    subnetwork = google_compute_subnetwork.compute_subnetwork.id
    network_ip = "10.2.0.1"
    alias_ip_range {
      ip_cidr_range = "/16"
      subnetwork_range_name = "sub-range"
    }
  }
  disk {
    auto_delete = false
    source = google_compute_disk.compute_disk.name
    boot = true
    interface = "SCSI"
    labels = {
      env = "dev"
    }
  }
  disk {
    auto_delete = true
    type = "PERSISTENT"
    device_name = "attachment"
    interface = "SCSI"
    disk_name = "sample-attached-disk"
    source_image = google_compute_image.compute_image.id
    disk_size_gb = 10
    disk_type = "pd-ssd"
    labels = {
      env = "dev"
    }
  }
  service_account {
    email = "cnrm-system@tjr-dm-test-1.iam.gserviceaccount.com"
    scopes = [
      "https://www.googleapis.com/auth/compute.readonly",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/userinfo.email"
    ]
  }
  scheduling {
    on_host_maintenance = "MIGRATE"
    automatic_restart = true
    preemptible = false
  }
  guest_accelerator {
    count = 1
    type = "nvidia-tesla-k80"
  }
  shielded_instance_config {
    enable_secure_boot = false
    enable_vtpm = true
    enable_integrity_monitoring = true
  }

  depends_on = [
    google_compute_disk.compute_disk,
    google_compute_image.compute_image,
    google_compute_network.compute_network,
    google_compute_subnetwork.compute_subnetwork
  ]
}

#tfimport-terraform import google_compute_instance_template.compute_beta_instancetemplate  __project__/compute-beta-instancetemplate
resource "google_compute_instance_template" "compute_beta_instancetemplate" {
  provider = google-beta

  description = "a sample  beta instance template"
  instance_description = "a sample beta instance created from the sample instance template"
  tags = [
    "foo",
    "bar"
  ]
  machine_type = "n1-standard-1"
  min_cpu_platform = "Intel Skylake"
  labels = {
    env = "dev"
  }
  network_interface {
    network = google_compute_network.compute_network.id
    subnetwork = google_compute_subnetwork.compute_subnetwork.id
    network_ip = "10.2.0.1"
    alias_ip_range {
      ip_cidr_range = "/16"
      subnetwork_range_name = "sub-range"
    }
  }
  disk {
    auto_delete = false
    source = google_compute_disk.compute_disk.name
    boot = true
    interface = "SCSI"
    labels = {
      env = "dev"
    }
  }
  disk {
    auto_delete = true
    type = "PERSISTENT"
    device_name = "attachment"
    interface = "SCSI"
    disk_name = "sample-attached-disk"
    source_image = google_compute_image.compute_image.id
    disk_size_gb = 10
    disk_type = "pd-ssd"
    labels = {
      env = "dev"
    }
  }
  service_account {
    email = "cnrm-system@tjr-dm-test-1.iam.gserviceaccount.com"
    scopes = [
      "https://www.googleapis.com/auth/compute.readonly",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/userinfo.email"
    ]
  }
  scheduling {
    on_host_maintenance = "MIGRATE"
    automatic_restart = true
    preemptible = false
  }
  guest_accelerator {
    count = 1
    type = "nvidia-tesla-k80"
  }
  shielded_instance_config {
    enable_secure_boot = false
    enable_vtpm = true
    enable_integrity_monitoring = true
  }

  depends_on = [
    google_compute_disk.compute_disk,
    google_compute_image.compute_image,
    google_compute_network.compute_network,
    google_compute_subnetwork.compute_subnetwork
  ]
}
