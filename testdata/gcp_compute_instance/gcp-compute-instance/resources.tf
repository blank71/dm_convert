provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_resource_policy.vm_placementpolicy_spread  __project__/us-west1/vm-placementpolicy-spread
resource "google_compute_resource_policy" "vm_placementpolicy_spread" {
  provider = google-beta

  name = "vm-placementpolicy-spread"
  description = "test-description"
  region = "us-west1"
  group_placement_policy {
    availability_domain_count = 3
  }
}

#tfimport-terraform import google_compute_disk.compute_disk_1  __project__/us-west1-a/compute-disk-1
resource "google_compute_disk" "compute_disk_1" {
  provider = google-beta

  name = "compute-disk-1"
  description = "a sample encrypted, blank disk"
  size = 1
  zone = "us-west1-a"
  physical_block_size_bytes = 4096
  type = "pd-ssd"
}

#tfimport-terraform import google_compute_disk.compute_disk_2  __project__/us-west1-a/compute-disk-2
resource "google_compute_disk" "compute_disk_2" {
  provider = google-beta

  name = "compute-disk-2"
  size = 1
  zone = "us-west1-a"
  type = "pd-ssd"
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
  ip_cidr_range = "10.2.0.0/16"
  region = "us-west1"
  network = google_compute_network.compute_network.id
  secondary_ip_range {
    ip_cidr_range = "10.3.16.0/20"
    range_name = "cloudrange"
  }

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_instance.compute_instance  __project__/us-west1-a/compute-instance
resource "google_compute_instance" "compute_instance" {
  provider = google-beta

  name = "compute-instance"
  can_ip_forward = false
  zone = "us-west1-a"
  machine_type = "n1-standard-1"
  tags = [
    "sap-hanaexpress-public-1-tcp-22"
  ]
  labels = {
    created-from = "image"
    network-type = "subnetwork"
  }
  boot_disk {
    auto_delete = false
    initialize_params {
      labels = {
        data-source = "external"
        schema-type = "auto-junk"
      }
      size = 24
      image = "projects/debian-cloud/global/images/family/debian-11"
      type = "pd-ssd"
    }
  }
  attached_disk {
    device_name = "proxycontroldisk"
    mode = "READ_ONLY"
    source = google_compute_disk.compute_disk_1.id
  }
  attached_disk {
    device_name = "persistentdisk"
    mode = "READ_WRITE"
    source = google_compute_disk.compute_disk_2.id
  }
  network_interface {
    subnetwork = google_compute_subnetwork.compute_subnetwork.id
    alias_ip_range {
      ip_cidr_range = "/24"
      subnetwork_range_name = "cloudrange"
    }
  }
  metadata = {
    foo = "bar"
  }
  resource_policies = [
    google_compute_resource_policy.vm_placementpolicy_spread.id
  ]
  scheduling {
    automatic_restart = false
    preemptible = true
    instance_termination_action = "STOP"
    provisioning_model = "SPOT"
  }
  shielded_instance_config {
    enable_integrity_monitoring = false
    enable_secure_boot = false
    enable_vtpm = true
  }
  enable_display = false

  depends_on = [
    google_compute_disk.compute_disk_1,
    google_compute_disk.compute_disk_2,
    google_compute_subnetwork.compute_subnetwork,
    google_compute_resource_policy.vm_placementpolicy_spread
  ]
}

#tfimport-terraform import google_compute_instance.compute_instance_1  __project__/us-west1-a/compute-instance-1
resource "google_compute_instance" "compute_instance_1" {
  provider = google-beta

  name = "compute-instance-1"
  min_cpu_platform = "Intel Cascade Lake"
  zone = "us-west1-a"
  machine_type = "n2-standard-32"
  boot_disk {
    auto_delete = false
    initialize_params {
      size = 24
      image = "projects/debian-cloud/global/images/family/debian-11"
      type = "pd-ssd"
    }
  }
  network_interface {
    alias_ip_range {
      ip_cidr_range = "/24"
    }
  }
  reservation_affinity {
    type = "SPECIFIC_RESERVATION"
    specific_reservation{
      key = "compute.googleapis.com/reservation-name"
      values = [
        "reservation-01"
      ]
    }
  }
}

#tfimport-terraform import google_compute_instance.compute_instance_2  __project__/us-west1-a/compute-instance-2
resource "google_compute_instance" "compute_instance_2" {
  provider = google-beta

  name = "compute-instance-2"
  min_cpu_platform = "AMD Rome"
  zone = "us-west1-a"
  machine_type = "n2d-standard-2"
  boot_disk {
    auto_delete = false
    initialize_params {
      size = 24
      image = "projects/debian-cloud/global/images/family/debian-11"
      type = "pd-ssd"
    }
  }
  network_interface {
    alias_ip_range {
      ip_cidr_range = "/24"
    }
  }
  scheduling {
    automatic_restart = true
    on_host_maintenance = "TERMINATE"
    preemptible = false
  }
  confidential_instance_config {
    enable_confidential_compute = true
  }
}

#tfimport-terraform import google_compute_instance.compute_instance_3  __project__/us-west1-a/compute-instance-3
resource "google_compute_instance" "compute_instance_3" {
  provider = google-beta

  name = "compute-instance-3"
  min_cpu_platform = "AMD Rome"
  zone = "us-west1-a"
  machine_type = "n2d-standard-2"
  boot_disk {
    auto_delete = false
    initialize_params {
      size = 24
      image = "projects/debian-cloud/global/images/family/debian-11"
      type = "pd-ssd"
    }
  }
  network_interface {
    alias_ip_range {
      ip_cidr_range = "/24"
    }
  }
  advanced_machine_features {
      enable_nested_virtualization = true
      threads_per_core = 1
      visible_core_count = 1
  }
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.networkInterfaces.accessConfigs.type: ['ONE_TO_ONE_NAT']
# properties.networkInterfaces.accessConfigs.name: ['external-nat']
#
#tfimport-terraform import google_compute_instance.compute_instance_4  __project__/us-west1-a/compute-instance-4
resource "google_compute_instance" "compute_instance_4" {
  provider = google-beta

  name = "compute-instance-4"
  min_cpu_platform = "Intel Cascade Lake"
  zone = "us-west1-a"
  machine_type = "n2-standard-32"
  boot_disk {
    auto_delete = false
    initialize_params {
      size = 24
      image = "https://www.googleapis.com/compute/beta/projects/debian-cloud/global/images/debian-11-bullseye-v20230629"
      type = "pd-ssd"
    }
  }
  network_interface {
    access_config {
    }
  }
  network_performance_config {
    total_egress_bandwidth_tier = "TIER_1"
  }
}

#tfimport-terraform import google_compute_network.compute_network_1  __project__/compute-network-1
resource "google_compute_network" "compute_network_1" {
  provider = google-beta

  name = "compute-network-1"
  auto_create_subnetworks = false
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork_1 __project__/us-west1/compute-subnetwork-1
resource "google_compute_subnetwork" "compute_subnetwork_1" {
  provider = google-beta

  name = "compute-subnetwork-1"
  ip_cidr_range = "10.1.0.0/20"
  region = "us-west1"
  ipv6_access_type = "EXTERNAL"
  stack_type = "IPV4_IPV6"
  network = google_compute_network.compute_network.id

  depends_on = [
    google_compute_network.compute_network_1
  ]
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.networkInterfaces.ipv6AccessConfigs.type: ['DIRECT_IPV6']
#
#tfimport-terraform import google_compute_instance.compute_instance_5  __project__/us-west1-a/compute-instance-5
resource "google_compute_instance" "compute_instance_5" {
  provider = google-beta

  name = "compute-instance-5"
  min_cpu_platform = "Intel Cascade Lake"
  zone = "us-west1-a"
  machine_type = "n2-standard-32"
  boot_disk {
    auto_delete = false
    initialize_params {
      size = 24
      image = "https://www.googleapis.com/compute/beta/projects/debian-cloud/global/images/debian-11-bullseye-v20230629"
      type = "pd-ssd"
    }
  }
  network_interface {
    network = google_compute_network.compute_network.id
    subnetwork = google_compute_subnetwork.compute_subnetwork.id
    queue_count = 1
    stack_type = "IPV4_IPV6"
    access_config {
      network_tier = "PREMIUM"
    }
    ipv6_access_config {
      network_tier = "PREMIUM"
      public_ptr_domain_name = "test.com."
    }
  }

  depends_on = [
    google_compute_subnetwork.compute_subnetwork_1,
    google_compute_network.compute_network_1
  ]
}

#tfimport-terraform import google_compute_instance.compute_instance_6  __project__/us-west1-a/compute-instance-6
resource "google_compute_instance" "compute_instance_6" {
  provider = google-beta

  name = "compute-instance-6"
  zone = "us-west1-a"
  machine_type = "n1-standard-1"
  boot_disk {
    auto_delete = true
    initialize_params {
      size = 24
      image = "projects/debian-cloud/global/images/family/debian-11"
      type = "pd-ssd"
    }
  }
  network_interface {
    alias_ip_range {
      ip_cidr_range = "/24"
    }
  }
  scheduling {
    automatic_restart = true
    on_host_maintenance = "TERMINATE"
    preemptible = false
    node_affinities {
      key = "color"
      operator = "IN"
      values = [
        "blue"
      ]
    }
  }
}
