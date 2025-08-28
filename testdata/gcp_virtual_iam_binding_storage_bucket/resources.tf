provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_storage_bucket_iam_member.virtual_iam_member_binding_storage_bucket  "b/my-test-bucket roles/storage.objectViewer user:user1@google.com"
resource "google_storage_bucket_iam_member" "virtual_iam_member_binding_storage_bucket" {
  provider = google-beta

  bucket = "my-test-bucket"
  role = "roles/storage.objectViewer"
  member = "user:user1@google.com"
}
