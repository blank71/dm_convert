provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_storage_bucket.tjr_dm_test_1_bucket  __project__/tjr-dm-test-1-bucket
resource "google_storage_bucket" "tjr_dm_test_1_bucket" {
  provider = google-beta

  name = "tjr-dm-test-1-bucket"
  location = "US"
}

#tfimport-terraform import google_storage_bucket_access_control.storage_bucketaccesscontrol  tjr-dm-test-1-bucket/allAuthenticatedUsers
resource "google_storage_bucket_access_control" "storage_bucketaccesscontrol" {
  provider = google-beta

  bucket = "tjr-dm-test-1-bucket"
  entity = "allAuthenticatedUsers"
  role = "READER"
}
