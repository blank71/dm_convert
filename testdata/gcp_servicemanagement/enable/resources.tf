provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project.test_project  test-project-id
resource "google_project" "test_project" {
  provider = google-beta

  name = "test-project"
  project_id = "test-project-id"
  org_id = "12345678910"
}

resource "google_project_service" "service_management_enable_action" {
  provider = google-beta

  service = "cloudbuild.googleapis.com"
  project = "test-project-id"
  disable_on_destroy = false

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }

  depends_on = [
    google_project.test_project
  ]
}
#tfimport-terraform import google_project_service.service_management_enable_action  test-project-id/cloudbuild.googleapis.com
