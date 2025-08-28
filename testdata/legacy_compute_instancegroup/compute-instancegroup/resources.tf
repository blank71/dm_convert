provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_instance_group.compute_instancegroup  __project__/us-west1-a/compute-instancegroup
resource "google_compute_instance_group" "compute_instancegroup" {
  provider = google-beta

  name = "compute-instancegroup"
  description = "Compute instance group with two specified instances and named http and https ports."
  zone = "us-west1-a"
  named_port {
    name = "http"
    port = 8080
  }
  named_port {
    name = "https"
    port = 8443
  }
}

#tfimport-terraform import google_compute_instance_group.compute_beta_instancegroup  __project__/us-west1-a/compute-beta-instancegroup
resource "google_compute_instance_group" "compute_beta_instancegroup" {
  provider = google-beta

  name = "compute-beta-instancegroup"
  description = "Compute beta instance group with two specified instances and named http and https ports."
  zone = "us-west1-a"
  named_port {
    name = "http"
    port = 8080
  }
  named_port {
    name = "https"
    port = 8443
  }
}
