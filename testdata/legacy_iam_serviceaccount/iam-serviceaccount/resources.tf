provider "google-beta" {
  project = "None"
}

resource "google_service_account" "iam_serviceaccount" {
  provider = google-beta

  account_id = "iam-serviceaccount"
  display_name = "Example Service Account"
  project = "test-project"
}
#tfimport-terraform import google_service_account.iam_serviceaccount  projects/test-project/serviceAccounts/iam-serviceaccount@test-project.iam.gserviceaccount.com
