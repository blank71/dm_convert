provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_storage_bucket.my_test_bucket_2  __project__/my-test-bucket-2
resource "google_storage_bucket" "my_test_bucket_2" {
  provider = google-beta

  name = "my-test-bucket-2"
  location = "US"
  storage_class = "STANDARD"
}

#tfimport-terraform import google_storage_bucket_iam_member.virtual_iam_member_binding_storage_bucket  "b/my-test-bucket roles/storage.objectViewer user:user1@google.com"
resource "google_storage_bucket_iam_member" "virtual_iam_member_binding_storage_bucket" {
  provider = google-beta

  bucket = "my-test-bucket"
  role = "roles/storage.objectViewer"
  member = "user:user1@google.com"
}

#tfimport-terraform import google_storage_bucket_iam_member.virtual_iam_member_binding_storage_bucket_2  "b/my-test-bucket-2 roles/storage.objectAdmin user:user2@google.com"
resource "google_storage_bucket_iam_member" "virtual_iam_member_binding_storage_bucket_2" {
  provider = google-beta

  bucket = google_storage_bucket.my_test_bucket_2.name
  role = "roles/storage.objectAdmin"
  member = "user:user2@google.com"

  depends_on = [
    google_storage_bucket.my_test_bucket_2
  ]
}
