provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_bigquery_dataset.bigquerydataset  tjr-dm-test-1/bigquerydataset
resource "google_bigquery_dataset" "bigquerydataset" {
  provider = google-beta

  default_table_expiration_ms = 3600000
  location = "us-west1"
  project = "tjr-dm-test-1"
  dataset_id = "bigquerydataset"
  access {
    role = "OWNER"
    user_by_email = "thomasrodgers@google.com"
  }
}
