provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_instance_template.template_test_deployment  __project__/template-test-deployment
resource "google_compute_instance_template" "template_test_deployment" {
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
    disk_name = "test-deployment-disk"
    source_image = "projects/debian-cloud/global/images/debian-7-wheezy-v20140619"
  }
}

#tfimport-terraform import google_compute_instance_group_manager.igm_test_deployment_1  __project__/us-west1-a/igm-test-deployment-1
resource "google_compute_instance_group_manager" "igm_test_deployment_1" {
  provider = google-beta

  base_instance_name = "test-deployment-instance"
  target_size = 1
  zone = "us-west1-a"
  name = "igm-test-deployment-1"
  version {
    instance_template = google_compute_instance_template.template_test_deployment.id
  }

  depends_on = [
    google_compute_instance_template.template_test_deployment
  ]
}

#tfimport-terraform import google_compute_autoscaler.autoscaler_test_deployment_1 __project__/us-west1-a/autoscaler-test-deployment-1
resource "google_compute_autoscaler" "autoscaler_test_deployment_1" {
  provider = google-beta

  name = "autoscaler-test-deployment-1"
  target = google_compute_instance_group_manager.igm_test_deployment_1.id
  description = "Autoscaler created for cloud config testing purposes"
  zone = "us-west1-a"
  autoscaling_policy {
    min_replicas = 1
    max_replicas = 3
    cooldown_period = 60
    cpu_utilization {
      target = 0.8
    }
  }
}

#tfimport-terraform import google_compute_instance_group_manager.igm_test_deployment_2  __project__/us-west1-a/igm-test-deployment-2
resource "google_compute_instance_group_manager" "igm_test_deployment_2" {
  provider = google-beta

  base_instance_name = "test-deployment-instance"
  target_size = 1
  zone = "us-west1-a"
  name = "igm-test-deployment-2"
  version {
    instance_template = google_compute_instance_template.template_test_deployment.id
  }

  depends_on = [
    google_compute_instance_template.template_test_deployment
  ]
}

#tfimport-terraform import google_compute_autoscaler.autoscaler_test_deployment_2 __project__/us-west1-a/autoscaler-test-deployment-2
resource "google_compute_autoscaler" "autoscaler_test_deployment_2" {
  provider = google-beta

  name = "autoscaler-test-deployment-2"
  target = google_compute_instance_group_manager.igm_test_deployment_2.id
  description = "Autoscaler created for cloud config testing purposes"
  zone = "us-west1-a"
  autoscaling_policy {
    min_replicas = 1
    max_replicas = 3
    cooldown_period = 60
    cpu_utilization {
      target = 0.8
    }
  }
}

#tfimport-terraform import google_compute_instance_group_manager.igm_test_deployment_3  __project__/us-west1-a/igm-test-deployment-3
resource "google_compute_instance_group_manager" "igm_test_deployment_3" {
  provider = google-beta

  base_instance_name = "test-deployment-instance"
  target_size = 1
  zone = "us-west1-a"
  name = "igm-test-deployment-3"
  version {
    instance_template = google_compute_instance_template.template_test_deployment.id
  }

  depends_on = [
    google_compute_instance_template.template_test_deployment
  ]
}

#tfimport-terraform import google_compute_autoscaler.autoscaler_test_deployment_3 __project__/us-west1-a/autoscaler-test-deployment-3
resource "google_compute_autoscaler" "autoscaler_test_deployment_3" {
  provider = google-beta

  name = "autoscaler-test-deployment-3"
  target = google_compute_instance_group_manager.igm_test_deployment_3.id
  description = "Autoscaler created for cloud config testing purposes"
  zone = "us-west1-a"
  autoscaling_policy {
    min_replicas = 1
    max_replicas = 3
    cooldown_period = 60
    cpu_utilization {
      target = 0.8
    }
  }
}

#tfimport-terraform import google_compute_instance_group_manager.igm_test_deployment_4  __project__/us-west1-a/igm-test-deployment-4
resource "google_compute_instance_group_manager" "igm_test_deployment_4" {
  provider = google-beta

  base_instance_name = "test-deployment-instance"
  target_size = 1
  zone = "us-west1-a"
  name = "igm-test-deployment-4"
  version {
    instance_template = google_compute_instance_template.template_test_deployment.id
  }

  depends_on = [
    google_compute_instance_template.template_test_deployment
  ]
}

#tfimport-terraform import google_compute_autoscaler.autoscaler_test_deployment_4 __project__/us-west1-a/autoscaler-test-deployment-4
resource "google_compute_autoscaler" "autoscaler_test_deployment_4" {
  provider = google-beta

  name = "autoscaler-test-deployment-4"
  target = google_compute_instance_group_manager.igm_test_deployment_4.id
  description = "Autoscaler created for cloud config testing purposes"
  zone = "us-west1-a"
  autoscaling_policy {
    min_replicas = 1
    max_replicas = 3
    cooldown_period = 60
    cpu_utilization {
      target = 0.8
    }
  }
}
