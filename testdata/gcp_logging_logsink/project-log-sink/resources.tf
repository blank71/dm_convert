provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic_resource  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic_resource" {
  provider = google-beta

  name = "pubsub-topic"
}

#tfimport-terraform import google_project.rm_project  rm-project
resource "google_project" "rm_project" {
  provider = google-beta

  name = "Project Sink Project"
  project_id = "rm-project"
  folder_id = "613349442449"
}

#tfimport-terraform import google_project_iam_member.rm_iammemberbinding  "rm-project roles/editor user:thomasrodgers@google.com"
resource "google_project_iam_member" "rm_iammemberbinding" {
  provider = google-beta

  project = "rm-project"
  role = "roles/editor"
  member = "user:thomasrodgers@google.com"
}

resource "google_project_service" "deploymentmanager_enable_service" {
  provider = google-beta

  service = "logging.googleapis.com"
  project = "rm-project"
  disable_on_destroy = false

  depends_on = [
    google_project.rm_project
  ]
}
#tfimport-terraform import google_project_service.deploymentmanager_enable_service  rm-project/logging.googleapis.com

resource "google_project_service" "deploymentmanager_enable_service_with_postfix" {
  provider = google-beta

  service = "api.googleapis.com"
  project = "rm-project"
  disable_on_destroy = false

  depends_on = [
    google_project.rm_project
  ]
}
#tfimport-terraform import google_project_service.deploymentmanager_enable_service_with_postfix  rm-project/api.googleapis.com

#tfimport-terraform import google_logging_project_sink.logging_sink projects/rm-project/sinks/logging-sink
resource "google_logging_project_sink" "logging_sink" {
  provider = google-beta

  project = "rm-project"
  unique_writer_identity = true
  destination = google_pubsub_topic.pubsub_topic_resource.name
  filter = "resource.type=\"bigquery_project\" AND logName:\"cloudaudit.googleapis.com\""
  name = "logging-sink"

  depends_on = [
    google_project.rm_project,
    google_project_service.deploymentmanager_enable_service,
    google_pubsub_topic.pubsub_topic_resource
  ]
}
