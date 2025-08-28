provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_region_autoscaler.autoscaler_sample  __project__/us-central1/autoscaler-sample
resource "google_compute_region_autoscaler" "autoscaler_sample" {
  provider = google-beta

  name = "autoscaler-sample"
  target = "ref_to_app"
  region = "us-central1"
  autoscaling_policy {
   min_replicas = 3
   max_replicas = 10
    cpu_utilization {
      target = 0.6
    }
  }
}

#tfimport-terraform import google_compute_instance_template.instance_template  __project__/instance-template
resource "google_compute_instance_template" "instance_template" {
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
    disk_name = "disk"
    source_image = "projects/debian-cloud/global/images/debian-7-wheezy-v20140619"
  }
}

#tfimport-terraform import google_compute_region_instance_group_manager.region_instance_group_managers  __project__/us-west1/region-instance-group-managers
resource "google_compute_region_instance_group_manager" "region_instance_group_managers" {
  provider = google-beta

  base_instance_name = "base-instance"
  target_size = 1
  region = "us-west1"
  name = "region-instance-group-managers"
  version {
    instance_template = google_compute_instance_template.instance_template.id
  }

  depends_on = [
    google_compute_instance_template.instance_template
  ]
}

#tfimport-terraform import google_compute_region_autoscaler.region_autoscaler  __project__/us-west1/region-autoscaler
resource "google_compute_region_autoscaler" "region_autoscaler" {
  provider = google-beta

  name = "region-autoscaler"
  description = "Autoscaler created for cloud config testing purposes"
  target = google_compute_region_instance_group_manager.region_instance_group_managers.id
  region = "us-west1"
  autoscaling_policy {
   min_replicas = 1
   max_replicas = 3
    cooldown_period = 60
    cpu_utilization {
      target = 0.8
    }
  }

  depends_on = [
    google_compute_region_instance_group_manager.region_instance_group_managers
  ]
}
