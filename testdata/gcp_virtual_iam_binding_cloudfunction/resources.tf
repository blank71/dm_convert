provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_cloudfunctions_function_iam_member.virtual_iam_member_binding_cloudfunctions "projects/test-project/locations/us-central1/functions/test-function roles/cloudfunctions.invoker user:user1@google.com"
resource "google_cloudfunctions_function_iam_member" "virtual_iam_member_binding_cloudfunctions" {
  provider = google-beta

  cloud_function = "projects/test-project/locations/us-central1/functions/test-function"
  role = "roles/cloudfunctions.invoker"
  member = "user:user1@google.com"
}
