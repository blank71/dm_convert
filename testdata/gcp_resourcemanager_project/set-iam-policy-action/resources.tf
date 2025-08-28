provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project.test_project  project-id
resource "google_project" "test_project" {
  provider = google-beta

  name = "test-project"
  project_id = "project-id"
  org_id = "123456789"
}

data "google_iam_policy" "set_iam_policy_completely_iam_policy" {
  binding {
    role = "roles/editor"
    members = [
      "serviceAccount:service-account@testdomain.com",
    ]
  }
  binding {
    role = "roles/deploymentmanager.editor"
    members = [
      "user:user@testdomain.com",
    ]
  }
  binding {
    role = "roles/deploymentmanager.editor"
    members = [
      "group:group@testdomain.com",
    ]
  }
  binding {
    role = "roles/appengine.codeViewer"
    members = [
    ]
  }
}

#tfimport-terraform import google_project_iam_policy.set_iam_policy_completely_iam_policy  google_project.test_project.project_id
resource "google_project_iam_policy" "set_iam_policy_completely_iam_policy" {
  project     = google_project.test_project.project_id
  policy_data = data.google_iam_policy.set_iam_policy_completely_iam_policy.policy_data
}
