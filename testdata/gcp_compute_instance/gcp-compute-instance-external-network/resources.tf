provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_instance.vm_created_by_deployment_manager  __project__/us-central1-a/vm-created-by-deployment-manager
resource "google_compute_instance" "vm_created_by_deployment_manager" {
  provider = google-beta

  name = "vm-created-by-deployment-manager"
  zone = "us-central1-a"
  machine_type = "n1-standard-1"
  boot_disk {
    device_name = "boot"
    auto_delete = true
    initialize_params {
      image = "projects/debian-cloud/global/images/family/debian-11"
    }
  }
  network_interface {
    network = "global/networks/default"
  }
}
