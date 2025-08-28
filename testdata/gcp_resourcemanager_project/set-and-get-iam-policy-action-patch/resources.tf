provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project_iam_member.patch_iam_policy_0  "test-project-id roles/composer.admin user:composer-admin@testdomain.com"
resource "google_project_iam_member" "patch_iam_policy_0" {
  provider = google-beta

  project = "test-project-id"
  role = "roles/composer.admin"
  member = "user:composer-admin@testdomain.com"
}

#tfimport-terraform import google_project_iam_member.patch_iam_policy_1  "test-project-id roles/compute.admin group:compute-admins@testdomain.com"
resource "google_project_iam_member" "patch_iam_policy_1" {
  provider = google-beta

  project = "test-project-id"
  role = "roles/compute.admin"
  member = "group:compute-admins@testdomain.com"
}

#tfimport-terraform import google_project_iam_member.patch_iam_policy_2  "test-project-id roles/owner group:owner@testdomain.com"
resource "google_project_iam_member" "patch_iam_policy_2" {
  provider = google-beta

  project = "test-project-id"
  role = "roles/owner"
  member = "group:owner@testdomain.com"
}

#tfimport-terraform import google_project_iam_member.patch_iam_policy_3  "test-project-id roles/viewer group:viewer1@testdomain.com"
resource "google_project_iam_member" "patch_iam_policy_3" {
  provider = google-beta

  project = "test-project-id"
  role = "roles/viewer"
  member = "group:viewer1@testdomain.com"
}

#tfimport-terraform import google_project_iam_member.patch_iam_policy_4  "test-project-id roles/viewer group:viewer2@testdomain.com"
resource "google_project_iam_member" "patch_iam_policy_4" {
  provider = google-beta

  project = "test-project-id"
  role = "roles/viewer"
  member = "group:viewer2@testdomain.com"
}
