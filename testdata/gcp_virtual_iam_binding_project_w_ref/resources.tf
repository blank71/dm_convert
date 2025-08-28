provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project.test_gcp_project  test-gcp-project-1234
resource "google_project" "test_gcp_project" {
  provider = google-beta

  name = "test-gcp-project"
  project_id = "test-gcp-project-1234"
  folder_id = "223456789101"
}

#tfimport-terraform import google_project_iam_member.iam_member_001  "test-gcp-project-1234 roles/storage.admin serviceAccount:$(ref.test-gcp-project.projectNumber)@cloudservices.gserviceaccount.com"
resource "google_project_iam_member" "iam_member_001" {
  provider = google-beta

  project = google_project.test_gcp_project.project_id
  role = "roles/storage.admin"
  member = "serviceAccount:$(ref.test-gcp-project.projectNumber)@cloudservices.gserviceaccount.com"
}
