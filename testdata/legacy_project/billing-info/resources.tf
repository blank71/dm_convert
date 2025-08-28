provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project.my_test_project  my-test-project
resource "google_project" "my_test_project" {
  provider = google-beta

  name = "my-test-project"
  project_id = "my-test-project"
  org_id = "119612413569"
  billing_account = "000000-AAAAFF-123456"
}
