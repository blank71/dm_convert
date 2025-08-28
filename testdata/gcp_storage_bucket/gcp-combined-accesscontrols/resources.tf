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
}
resource "google_storage_bucket_acl" "tjr_dm_test_1_bucket_acl" {
  provider = google-beta

  bucket      = google_storage_bucket.tjr_dm_test_1_bucket.name
  role_entity = [
    "READER:allAuthenticatedUsers",
  ]
}
resource "google_storage_default_object_acl" "tjr_dm_test_1_bucket_default_object_acl" {
  provider = google-beta

  bucket      = google_storage_bucket.tjr_dm_test_1_bucket.name
  role_entity = [
    "READER:allAuthenticatedUsers",
  ]
}
