provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic" {
  provider = google-beta

  name = "pubsub-topic"

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }
}

#tfimport-terraform import google_pubsub_topic.gcp_pubsub_topic_insert_action_test  __project__/test-topic-name
resource "google_pubsub_topic" "gcp_pubsub_topic_insert_action_test" {
  provider = google-beta

  labels = {
    label1 = "label1-val"
    label2 = "label2-val"
  }
  name = "test-topic-name"
  kms_key_name = "projects/test-project/locations/us-central1/keyRings/testKeyRing/cryptoKeys/testCryptoKey"
  message_storage_policy {
    allowed_persistence_regions = [
      "us-west1"
    ]
  }

  depends_on = [
    google_pubsub_topic.pubsub_topic
  ]
}
