provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_folder_iam_member.virtual_iam_member_binding_folder "virtual_iam_member_binding_folder roles/artifactregistry.admin user:user1@google.com"
resource "google_folder_iam_member" "virtual_iam_member_binding_folder" {
  provider = google-beta

  folder = "folders/12345"
  role = "roles/artifactregistry.admin"
  member = "user:user1@google.com"
}
