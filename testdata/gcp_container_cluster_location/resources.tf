provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_container_cluster.my_cluster __project__/us-central1/my-cluster
resource "google_container_cluster" "my_cluster" {
  provider = google-beta

  name = "my-cluster"
  network = "global/networks/default"
  subnetwork = "regions/us-central1/subnetworks/default"
  location = "us-central1"
  node_config {
    disk_size_gb = 10
    image_type = "projects/debian-cloud/global/images/family/debian-9"
  }
}
