provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_disk.compute_disk_access_control_test  __project__/us-central1-f/compute-disk-access-control-test
resource "google_compute_disk" "compute_disk_access_control_test" {
  provider = google-beta

  name = "compute-disk-access-control-test"
  size = 10
  zone = "us-central1-f"
  image = "projects/debian-cloud/global/images/family/debian-10"
}

data "google_iam_policy" "compute_disk_access_control_test_iam_policy" {
  binding {
    role = "roles/compute.storageAdmin"
    members = [
      "user:user1@google.com",
      "user:user2@google.com",
    ]
  }
  binding {
    role = "roles/compute.viewer"
    members = [
      "serviceAccount:test@test.iam.gserviceaccount.com",
    ]
  }
  binding {
    role = "roles/compute.admin"
    members = [
    ]
  }
}

#tfimport-terraform import google_compute_disk_iam_policy.compute_disk_access_control_test_policy __project__/us-central1-f/compute-disk-access-control-test
resource "google_compute_disk_iam_policy" "compute_disk_access_control_test_policy" {
  project        = google_compute_disk.compute_disk_access_control_test.project
  zone           = google_compute_disk.compute_disk_access_control_test.zone
  name           = google_compute_disk.compute_disk_access_control_test.name
  policy_data    = data.google_iam_policy.compute_disk_access_control_test_iam_policy.policy_data
}
