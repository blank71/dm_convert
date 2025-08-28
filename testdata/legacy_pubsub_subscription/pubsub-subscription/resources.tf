provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic" {
  provider = google-beta

  name = "pubsub-topic"
}

#tfimport-terraform import google_pubsub_subscription.pubsub_subscription  __project__/pubsub-subscription
resource "google_pubsub_subscription" "pubsub_subscription" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "pubsub-subscription"
  topic = google_pubsub_topic.pubsub_topic.name
  message_retention_duration = "86400s"
  retain_acked_messages = false
  ack_deadline_seconds = 15
  filter = "attributes.domain = \"com\""

  depends_on = [
    google_pubsub_topic.pubsub_topic
  ]
}
