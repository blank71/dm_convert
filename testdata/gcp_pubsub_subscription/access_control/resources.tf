provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_subscription.pubsub  __project__/my-pubsub-subscription
resource "google_pubsub_subscription" "pubsub" {
  provider = google-beta

  name = "my-pubsub-subscription"
  topic = "my-pubsub-topic"
}

data "google_iam_policy" "pubsub_iam_policy" {
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

#tfimport-terraform import google_pubsub_subscription_iam_policy.pubsub_policy __project__/my-pubsub-subscription
resource "google_pubsub_subscription_iam_policy" "pubsub_policy" {
  subscription   = google_pubsub_subscription.pubsub.name
  policy_data    = data.google_iam_policy.pubsub_iam_policy.policy_data
}
