provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic" {
  provider = google-beta

  name = "pubsub-topic"
}

resource "google_service_account" "iam_serviceaccount" {
  provider = google-beta

  account_id = "iam-serviceaccount"
}
#tfimport-terraform import google_service_account.iam_serviceaccount  projects/__project__/serviceAccounts/iam-serviceaccount@__project__.iam.gserviceaccount.com

#tfimport-terraform import google_project_iam_custom_role.iamrole projects/__project__/roles/iamrole
resource "google_project_iam_custom_role" "iamrole" {
  provider = google-beta

  role_id = "iamrole"
  description = "This role only contains two permissions - publish and update"
  permissions = [
    "pubsub.topics.publish",
    "pubsub.topics.update"
  ]
  stage = "GA"
  title = "Example Custom Role"
  project = "tjr-dm-test-1"
}
