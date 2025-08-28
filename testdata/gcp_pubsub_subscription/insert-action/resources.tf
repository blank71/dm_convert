provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic" {
  provider = google-beta

  name = "pubsub-topic"
}

#tfimport-terraform import google_pubsub_subscription.gcp_pubsub_subscription_insert_action_test  __project__/test-subscription-name
resource "google_pubsub_subscription" "gcp_pubsub_subscription_insert_action_test" {
  provider = google-beta

  labels = {
    label1 = "label1-val"
    label2 = "label2-val"
  }
  name = "test-subscription-name"
  topic = "projects/test-project/topics/pubsub-topic"
  message_retention_duration = "432000s"
  retain_acked_messages = true
  ack_deadline_seconds = 60
  expiration_policy {
    ttl = "432000s"
  }
  dead_letter_policy {
    dead_letter_topic = "projects/test-project/topics-dead-letter-dest-topic"
    max_delivery_attempts = 10
  }
  filter = "attributes:foo"
  enable_message_ordering = true

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }

  depends_on = [
    google_pubsub_topic.pubsub_topic
  ]
}
