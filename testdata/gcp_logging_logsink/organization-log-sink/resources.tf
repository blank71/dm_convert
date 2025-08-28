provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_storage_bucket.tjr_dm_test_1_bucket  __project__/tjr-dm-test-1-bucket
resource "google_storage_bucket" "tjr_dm_test_1_bucket" {
  provider = google-beta

  name = "tjr-dm-test-1-bucket"
  location = "US"
}

#tfimport-terraform import google_logging_organization_sink.logging_sink organizations/128653134652/sinks/logging-sink
resource "google_logging_organization_sink" "logging_sink" {
  provider = google-beta

  org_id = "128653134652"
  destination = google_storage_bucket.tjr_dm_test_1_bucket.name
  filter = "resource.type=\"bigquery_project\" AND logName:\"cloudaudit.googleapis.com\""
  name = "logging-sink"

  depends_on = [
    google_storage_bucket.tjr_dm_test_1_bucket
  ]
}
