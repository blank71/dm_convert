provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_logging_folder_sink.test_logging_sink folders/613349442449/sinks/bigquery_export
resource "google_logging_folder_sink" "test_logging_sink" {
  provider = google-beta

  folder = "613349442449"
  destination = "pubsub.googleapis.com/projects/test-project/topics/bigquery_export"
  filter = "protoPayload.serviceName:'bigquery.googleapis.com' protoPayload.methodName:'jobservice.jobcompleted'"
  name = "bigquery_export"
}
