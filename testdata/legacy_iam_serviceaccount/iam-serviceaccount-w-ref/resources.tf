provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project.sample_project  sample-project
resource "google_project" "sample_project" {
  provider = google-beta

  name = "sample-project"
  project_id = "sample-project"
  folder_id = "123"
}

resource "google_service_account" "iam_serviceaccount" {
  provider = google-beta

  account_id = "iam-serviceaccount"
  display_name = "Example Service Account"
  project = google_project.sample_project.project_id
}
#tfimport-terraform import google_service_account.iam_serviceaccount  projects/sample-project/serviceAccounts/iam-serviceaccount@sample-project.iam.gserviceaccount.com
