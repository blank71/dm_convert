provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "pubsub-topic"
  message_storage_policy {
    allowed_persistence_regions = [
      "us-west1"
    ]
  }
}
