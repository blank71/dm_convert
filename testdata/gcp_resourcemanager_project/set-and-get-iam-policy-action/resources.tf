provider "google-beta" {
  project = "None"
}

data "google_iam_policy" "patch_iam_policy_iam_policy" {
  binding {
    role = "roles/composer.admin"
    members = [
      "user:composer-admin@testdomain.com",
    ]
  }
  binding {
    role = "roles/compute.admin"
    members = [
      "group:compute-admins@testdomain.com",
    ]
  }
  binding {
    role = "roles/owner"
    members = [
      "group:owner@testdomain.com",
    ]
  }
  binding {
    role = "roles/viewer"
    members = [
      "group:viewer1@testdomain.com",
      "group:viewer2@testdomain.com",
    ]
  }
  binding {
    role = "roles/appengine.codeViewer"
    members = [
    ]
  }
}

#tfimport-terraform import google_project_iam_policy.patch_iam_policy_iam_policy  test-project-id
resource "google_project_iam_policy" "patch_iam_policy_iam_policy" {
  project     = "test-project-id"
  policy_data = data.google_iam_policy.patch_iam_policy_iam_policy.policy_data
}
