provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_cloudfunctions_function.my_function  __project__/asia-southeast2/my-function
resource "google_cloudfunctions_function" "my_function" {
  provider = google-beta

  name = "my-function"
  description = "Cloud Function"
  entry_point = "schema_change"
  runtime = "python37"
  max_instances = 1
  vpc_connector = "projects/my-project/locations/asia-southeast2/connectors/bi-app-vc"
  region = "asia-southeast2"
  timeout = 420
  source_archive_bucket = "my-bucket"
  source_archive_object = "cloud-function.zip"
  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource = "projects/my-project/topics/my-topic"
  }
  environment_variables = {
    "DEPLOYMENT_NAME" = "test-dep"
    "INSERT_FILTER_LIST" = ""
    "SP_BASE_URL" = "http://127.0.0.1"
    "TARGET_AUDIENCE" = "1234.apps.googleusercontent.com"
  }
}
