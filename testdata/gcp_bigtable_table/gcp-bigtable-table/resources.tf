provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_bigtable_instance.bigtable_instance  __project__/bigtable-instance
resource "google_bigtable_instance" "bigtable_instance" {
  provider = google-beta

  name = "bigtable-instance"
  cluster {
    cluster_id   = "bigtable-cluster-1"
    zone         = "us-central1-a"
    num_nodes    = 3
    storage_type = "SSD"
  }
  cluster {
    cluster_id   = "bigtable-cluster-2"
    zone         = "us-west1-a"
    num_nodes    = 3
    storage_type = "SSD"
  }
}

#tfimport-terraform import google_bigtable_table.bigtable_table  __project__/bigtable-table
resource "google_bigtable_table" "bigtable_table" {
  provider = google-beta

  name = "bigtable-table"
  instance_name = google_bigtable_instance.bigtable_instance.name

  depends_on = [
    google_bigtable_instance.bigtable_instance
  ]
}
