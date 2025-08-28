provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_instance.test_instance  __project__/us-central1-a/test-instance
resource "google_compute_instance" "test_instance" {
  provider = google-beta

  name = "test-instance"
  zone = "us-central1-a"
  machine_type = "n1-standard-1"
  boot_disk {
    initialize_params {
      image = "projects/debian-cloud/global/images/family/debian-11"
    }
  }
  network_interface {
    network = "global/networks/default"
    alias_ip_range {
      ip_cidr_range = "10.128.0.0/24"
    }
    alias_ip_range {
      ip_cidr_range = "10.129.0.0/24"
      subnetwork_range_name = "secondary-range-1"
    }
  }
}
