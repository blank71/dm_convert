provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_resource_for_testing_depends_on  __project__/some-topic
resource "google_pubsub_topic" "pubsub_resource_for_testing_depends_on" {
  provider = google-beta

  name = "some-topic"
}

data "google_project" "get_project_action_test" {
  project_id = "test-project-id"

  depends_on = [
    google_pubsub_topic.pubsub_resource_for_testing_depends_on
  ]
}
