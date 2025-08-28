provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_bigquery_dataset.bigquerydataset  tjr-dm-test-1/bigquerydataset
resource "google_bigquery_dataset" "bigquerydataset" {
  provider = google-beta

  default_table_expiration_ms = 3600000
  location = "us-west1"
  dataset_id = "bigquerydataset"
  project = "tjr-dm-test-1"
  access {
    role = "OWNER"
    user_by_email = "thomasrodgers@google.com"
  }
}

#tfimport-terraform import google_bigquery_table.bigquerytable  tjr-dm-test-1/bigquerydataset/bigquerytable
resource "google_bigquery_table" "bigquerytable" {
  provider = google-beta

  labels = {
    data-source = "external"
    schema-type = "auto-junk"
  }
  dataset_id = "bigquerydataset"
  project = "tjr-dm-test-1"
  table_id = "bigquerytable"

  depends_on = [
    google_bigquery_dataset.bigquerydataset
  ]
}
