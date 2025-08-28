provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project_iam_member.virtual_iam_member_binding_project  "my-test-project roles/artifactregistry.admin user:user1@google.com"
resource "google_project_iam_member" "virtual_iam_member_binding_project" {
  provider = google-beta

  project = "my-test-project"
  role = "roles/artifactregistry.admin"
  member = "user:user1@google.com"
}
