provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_storage_bucket.storage_bucket  __project__/storage-bucket
resource "google_storage_bucket" "storage_bucket" {
  provider = google-beta

  name = "storage-bucket"
  location = "US"
  versioning {
    enabled = true
  }
}

data "google_iam_policy" "bucket_set_iam_policy_iam_policy" {
  binding {
    role = "roles/storage.objectAdmin"
    members = [
      "serviceAccount:123456789@cloudservices.gserviceaccount.com",
    ]
  }
  binding {
    role = "roles/storage.objectViewer"
    members = [
      "group:groupname@testdomain.com",
    ]
  }
  binding {
    role = "roles/storage.objectAdmin"
    members = [
    ]
  }
  binding {
    role = "roles/storage.objectCreator"
    members = [
      "user:user1@testdomain.com",
    ]
  }
}

resource "google_storage_bucket_iam_policy" "bucket_set_iam_policy_iam_policy" {
  provider = google-beta
bucket = google_storage_bucket.storage_bucket.name
  policy_data = data.google_iam_policy.bucket_set_iam_policy_iam_policy.policy_data
}
#tfimport-terraform import google_storage_bucket_iam_policy.bucket_set_iam_policy_iam_policy  "b/google_storage_bucket.storage_bucket.name"
