provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_logging_project_sink.test_logging_sink projects/test-project/sinks/bigquery_export
resource "google_logging_project_sink" "test_logging_sink" {
  provider = google-beta

  project = "test-project"
  unique_writer_identity = true
  destination = "pubsub.googleapis.com/projects/test-project/topics/bigquery_export"
  filter = "protoPayload.serviceName:'bigquery.googleapis.com' protoPayload.methodName:'jobservice.jobcompleted'"
  name = "bigquery_export"
}
