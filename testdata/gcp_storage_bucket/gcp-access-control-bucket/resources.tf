provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_storage_bucket.gcp_storage_bucket_access_control_test  __project__/gcp-storage-bucket-access-control-test
resource "google_storage_bucket" "gcp_storage_bucket_access_control_test" {
  provider = google-beta

  name = "gcp-storage-bucket-access-control-test"
  location = "US"
  storage_class = "STANDARD"
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 7
    }
  }
}

data "google_iam_policy" "gcp_storage_bucket_access_control_test_iam_policy" {
  binding {
    role = "roles/storage.objectCreator"
    members = [
      "user:user1@google.com",
    ]
  }
  binding {
    role = "roles/storage.objectViewer"
    members = [
      "user:user1@google.com",
      "user:user2@google.com",
    ]
  }
  binding {
    role = "roles/storage.objectAdmin"
    members = [
    ]
  }
}

#tfimport-terraform import google_storage_bucket_iam_policy.gcp_storage_bucket_access_control_test_policy b/gcp-storage-bucket-access-control-test
resource "google_storage_bucket_iam_policy" "gcp_storage_bucket_access_control_test_policy" {
  bucket         = google_storage_bucket.gcp_storage_bucket_access_control_test.name
  policy_data    = data.google_iam_policy.gcp_storage_bucket_access_control_test_iam_policy.policy_data
}
