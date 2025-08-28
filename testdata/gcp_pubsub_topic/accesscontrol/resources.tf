provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic  __project__/my-pubsub-topic
resource "google_pubsub_topic" "pubsub_topic" {
  provider = google-beta

  name = "my-pubsub-topic"
}

data "google_iam_policy" "pubsub_topic_iam_policy" {
  binding {
    role = "roles/pubsub.editor"
    members = [
      "user:user1@google.com",
      "user:user2@google.com",
    ]
  }
  binding {
    role = "roles/pubsub.publisher"
    members = [
      "serviceAccount:test@test.iam.gserviceaccount.com",
    ]
  }
}

#tfimport-terraform import google_pubsub_topic_iam_policy.pubsub_topic_policy __project__/my-pubsub-topic
resource "google_pubsub_topic_iam_policy" "pubsub_topic_policy" {
  topic          = google_pubsub_topic.pubsub_topic.name
  policy_data    = data.google_iam_policy.pubsub_topic_iam_policy.policy_data
}
