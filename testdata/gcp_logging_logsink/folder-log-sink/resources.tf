provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_bigquery_dataset.bigquerydataset  tjr-dm-test-1/bigquerydataset
resource "google_bigquery_dataset" "bigquerydataset" {
  provider = google-beta

  location = "us-west1"
  dataset_id = "bigquerydataset"
  project = "tjr-dm-test-1"
}

#tfimport-terraform import google_logging_folder_sink.logging_sink folders/613349442449/sinks/logging-sink
resource "google_logging_folder_sink" "logging_sink" {
  provider = google-beta

  folder = "613349442449"
  destination = google_bigquery_dataset.bigquerydataset.dataset_id
  filter = "resource.type=\"bigquery_project\" AND logName:\"cloudaudit.googleapis.com\""
  name = "logging-sink"

  depends_on = [
    google_bigquery_dataset.bigquerydataset
  ]
}
