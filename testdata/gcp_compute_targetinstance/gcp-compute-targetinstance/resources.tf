provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork __project__/us-west1/compute-subnetwork
resource "google_compute_subnetwork" "compute_subnetwork" {
  provider = google-beta

  name = "compute-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region = "us-west1"
  network = google_compute_network.compute_network.id

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
  boot_disk {
    auto_delete = false
    initialize_params {
      image = "projects/debian-cloud/global/images/family/debian-11"
    }
  }
  network_interface {
    network = google_compute_network.compute_network.id
    subnetwork = google_compute_subnetwork.compute_subnetwork.id
  }

  depends_on = [
    google_compute_network.compute_network,
    google_compute_subnetwork.compute_subnetwork
  ]
}

#tfimport-terraform import google_compute_target_instance.compute_targetinstance __project__/us-west1-a/compute-targetinstance
resource "google_compute_target_instance" "compute_targetinstance" {
  provider = google-beta

  name = "compute-targetinstance"
  description = "Target instance, containing a VM instance which will have no NAT applied to it and can be used for protocol forwarding."
  instance = google_compute_instance.compute_instance.id
  zone = "us-west1-a"

  depends_on = [
    google_compute_instance.compute_instance
  ]
}
