provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_bigquery_dataset.bigquerydataset  __project__/bigquerydataset
resource "google_bigquery_dataset" "bigquerydataset" {
  provider = google-beta

  dataset_id = "bigquerydataset"
}
