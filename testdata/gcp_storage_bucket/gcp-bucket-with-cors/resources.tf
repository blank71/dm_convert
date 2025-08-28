provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_storage_bucket.tjr_dm_test_1_bucket  __project__/tjr-dm-test-1-bucket
resource "google_storage_bucket" "tjr_dm_test_1_bucket" {
  provider = google-beta

  name = "tjr-dm-test-1-bucket"
  location = "US"
  versioning {
    enabled = true
  }
  uniform_bucket_level_access = true
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
  }
}
