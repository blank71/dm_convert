provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_region_instance_group_manager.it_europe  __project__/europe-west4/it-europe
resource "google_compute_region_instance_group_manager" "it_europe" {
  provider = google-beta

  base_instance_name = "it"
  target_size = 1
  region = "europe-west4"
  name = "it-europe"
  version {
    instance_template = "projects/my-project/global/instanceTemplates/it-europe"
  }
  named_port {
    name = "front"
    port = 443
  }
  auto_healing_policies {
    health_check = "fake-health-check-self-link-here"
    initial_delay_sec = 900
  }
  update_policy {
    type = "PROACTIVE"
    minimal_action = "REPLACE"
    max_surge_percent = 1
    max_unavailable_fixed = 0
  }
  stateful_disk {
    device_name = "test-boot"
    delete_rule = "ON_PERMANENT_INSTANCE_DELETION"
  }
  stateful_disk {
    device_name = "test-data"
    delete_rule = "NEVER"
  }
}

#tfimport-terraform import google_compute_instance_template.demo_deployment_it  __project__/demo-deployment-it
resource "google_compute_instance_template" "demo_deployment_it" {
  provider = google-beta

  machine_type = "f1-micro"
  network_interface {
    network = "default"
  }
  disk {
    auto_delete = true
    type = "PERSISTENT"
    mode = "READ_WRITE"
    device_name = "boot"
    boot = true
    disk_name = "demo-deployment-disk"
    source_image = "https://www.googleapis.com/compute/v1/projects/debian-cloud/global/images/debian-7-wheezy-v20140619"
  }
}

#tfimport-terraform import google_compute_region_instance_group_manager.demo_deployment_igm_1  __project__/us-west1/demo-deployment-igm-1
resource "google_compute_region_instance_group_manager" "demo_deployment_igm_1" {
  provider = google-beta

  base_instance_name = "demo-deployment-instance"
  target_size = 1
  region = "us-west1"
  name = "demo-deployment-igm-1"
  version {
    instance_template = google_compute_instance_template.demo_deployment_it.id
  }

  depends_on = [
    google_compute_instance_template.demo_deployment_it
  ]
}

#tfimport-terraform import google_compute_region_instance_group_manager.demo_deployment_igm_2  __project__/us-west1/demo-deployment-igm-2
resource "google_compute_region_instance_group_manager" "demo_deployment_igm_2" {
  provider = google-beta

  base_instance_name = "demo-deployment-instance"
  target_size = 1
  region = "us-west1"
  name = "demo-deployment-igm-2"
  version {
    instance_template = google_compute_instance_template.demo_deployment_it.id
  }

  depends_on = [
    google_compute_instance_template.demo_deployment_it
  ]
}
