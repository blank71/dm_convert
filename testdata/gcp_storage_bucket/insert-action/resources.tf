provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic" {
  provider = google-beta

  name = "pubsub-topic"
}

#tfimport-terraform import google_storage_bucket.insert_action_test_actual_bucket_name  __project__/insert-action-test-actual-bucket-name
resource "google_storage_bucket" "insert_action_test_actual_bucket_name" {
  provider = google-beta

  name = "insert-action-test-actual-bucket-name"
  location = "US"
  retention_policy {
    retention_period = 3600
  }
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
  requester_pays = true
  cors {
    origin = [
      "http://example.appspot.com"
    ]
    method = [
      "GET",
      "HEAD",
      "DELETE"
    ]
    response_header = [
      "Content-Type"
    ]
    max_age_seconds = 3600
  }
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 7
    }
  }
  labels = {
    label-one = "value-one"
    label-two = "value-two"
  }

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }

  depends_on = [
    google_pubsub_topic.pubsub_topic
  ]
}
