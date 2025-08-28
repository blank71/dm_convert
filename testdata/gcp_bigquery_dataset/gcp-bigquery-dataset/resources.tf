provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_bigquery_dataset.bigquerydataset  tjr-dm-test-1/bigquerydataset
resource "google_bigquery_dataset" "bigquerydataset" {
  provider = google-beta

  description = "That's a bug"
  default_table_expiration_ms = 3600000
  location = "us-west1"
  dataset_id = "bigquerydataset"
  project = "tjr-dm-test-1"
  access {
    role = "OWNER"
    special_group = "projectOwners"
  }
  access {
    role = "OWNER"
    special_group = "projectWriters"
  }
}
