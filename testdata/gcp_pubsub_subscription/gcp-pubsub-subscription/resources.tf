provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic" {
  provider = google-beta

  labels = {
    tag = "dmv3-hackathon"
  }
  name = "pubsub-topic"
}

#tfimport-terraform import google_pubsub_topic.pubsub_dead_letter_topic  __project__/pubsub-dead-letter-topic
resource "google_pubsub_topic" "pubsub_dead_letter_topic" {
  provider = google-beta

  name = "pubsub-dead-letter-topic"
}

#tfimport-terraform import google_pubsub_subscription.pubsub_subscription_1  __project__/pubsub-subscription-1
resource "google_pubsub_subscription" "pubsub_subscription_1" {
  provider = google-beta

  name = "pubsub-subscription-1"
  topic = google_pubsub_topic.pubsub_topic.name

  depends_on = [
    google_pubsub_topic.pubsub_topic
  ]
}

#tfimport-terraform import google_pubsub_subscription.pubsub_subscription_2  __project__/pubsub-subscription-2
resource "google_pubsub_subscription" "pubsub_subscription_2" {
  provider = google-beta

  name = "pubsub-subscription-2"
  topic = google_pubsub_topic.pubsub_topic.name
  message_retention_duration = "86400s"
  retain_acked_messages = false
  ack_deadline_seconds = 15
  dead_letter_policy {
    dead_letter_topic = google_pubsub_topic.pubsub_dead_letter_topic.name
    max_delivery_attempts = 5
  }
  filter = "attributes.domain = \"com\""

  depends_on = [
    google_pubsub_topic.pubsub_topic
  ]
}
