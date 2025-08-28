provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic_resource  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic_resource" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "pubsub-topic"
}
