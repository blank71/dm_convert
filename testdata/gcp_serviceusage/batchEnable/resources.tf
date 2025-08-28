provider "google-beta" {
  project = "None"
}

resource "google_project_service" "batch_enable_services_action_appengine" {
  provider = google-beta

  service = "appengine.googleapis.com"
  project = "test-project-id"
  disable_on_destroy = false

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }
}
#tfimport-terraform import google_project_service.batch_enable_services_action_appengine  test-project-id/appengine.googleapis.com

resource "google_project_service" "batch_enable_services_action_bigtable" {
  provider = google-beta

  service = "bigtable.googleapis.com"
  project = "test-project-id"
  disable_on_destroy = false

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }
}
#tfimport-terraform import google_project_service.batch_enable_services_action_bigtable  test-project-id/bigtable.googleapis.com

resource "google_project_service" "batch_enable_services_action_cloudapis" {
  provider = google-beta

  service = "cloudapis.googleapis.com"
  project = "test-project-id"
  disable_on_destroy = false

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }
}
#tfimport-terraform import google_project_service.batch_enable_services_action_cloudapis  test-project-id/cloudapis.googleapis.com

resource "google_project_service" "batch_enable_services_action_cloudbilling" {
  provider = google-beta

  service = "cloudbilling.googleapis.com"
  project = "test-project-id"
  disable_on_destroy = false

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }
}
#tfimport-terraform import google_project_service.batch_enable_services_action_cloudbilling  test-project-id/cloudbilling.googleapis.com

resource "google_project_service" "batch_enable_services_action_cloudbuild" {
  provider = google-beta

  service = "cloudbuild.googleapis.com"
  project = "test-project-id"
  disable_on_destroy = false

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }
}
#tfimport-terraform import google_project_service.batch_enable_services_action_cloudbuild  test-project-id/cloudbuild.googleapis.com

resource "google_project_service" "batch_enable_services_action_cloudfunctions" {
  provider = google-beta

  service = "cloudfunctions.googleapis.com"
  project = "test-project-id"
  disable_on_destroy = false

  // Derived from action metadata.runtimePolicy = "CREATE"
  lifecycle {
    ignore_changes = all
  }
}
#tfimport-terraform import google_project_service.batch_enable_services_action_cloudfunctions  test-project-id/cloudfunctions.googleapis.com
