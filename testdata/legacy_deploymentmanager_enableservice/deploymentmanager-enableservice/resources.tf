provider "google-beta" {
  project = "None"
}

resource "google_project_service" "deploymentmanager_enable_service" {
  provider = google-beta

  service = "drive.googleapis.com"
  project = "tjr-dm-test-1"
  disable_on_destroy = false
}
#tfimport-terraform import google_project_service.deploymentmanager_enable_service  tjr-dm-test-1/drive.googleapis.com
