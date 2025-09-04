provider "google-beta" {
  project = "None"
}

resource "google_cloudbuild_trigger" "cloud_buildtrigger" {
  provider = google-beta

  
  name = "cloud-buildtrigger"
  description = "Cloud Build Trigger with a build template file. Builds the master branch of the referenced Cloud Source Repository."
  disabled = false
  filename = "cloudbuild.yaml"
  ignored_files = [
    "**/*.md"
  ]
  included_files = [
    "src/**"
  ]
  substitutions = {
    _SERVICE_NAME = "service-name"
  }
  trigger_template {
    repo_name = "projects/tjr-dm-test-1/repos/sourcerepo-repo"
    branch_name = "master"
    dir = "team-a/service-b"
  }
}
#tfimport-terraform import google_cloudbuild_trigger.cloud_buildtrigger projects/__project__/locations/global/triggers/cloud-buildtrigger
