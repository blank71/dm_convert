provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic_resource  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic_resource" {
  provider = google-beta

  labels = {
    subnetwork-name = data.google_compute_subnetwork.get_subnetwork_action.id
  }
  name = "pubsub-topic"
}

#tfimport-terraform import google_pubsub_topic.pubsub_resource_for_testing_depends_on  __project__/some-topic
resource "google_pubsub_topic" "pubsub_resource_for_testing_depends_on" {
  provider = google-beta

  name = "some-topic"
}

data "google_compute_subnetwork" "get_subnetwork_action" {
  name = "get-subnetwork-action"
  region = "us-west1"
  project = "test-project"

  depends_on = [
    google_pubsub_topic.pubsub_resource_for_testing_depends_on
  ]
}
