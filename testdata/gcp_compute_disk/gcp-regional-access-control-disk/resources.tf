provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_region_disk.compute_region_disk_access_control_test  __project__/us-west1/compute-region-disk-access-control-test
resource "google_compute_region_disk" "compute_region_disk_access_control_test" {
  provider = google-beta

  name = "compute-region-disk-access-control-test"
  region = "us-west1"
  replica_zones = [
    "zones/us-west1-a",
    "zones/us-west1-b"
  ]
  size = 200
}

data "google_iam_policy" "compute_region_disk_access_control_test_iam_policy" {
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

#tfimport-terraform import google_compute_region_disk_iam_policy.compute_region_disk_access_control_test_policy __project__/us-west1/compute-region-disk-access-control-test
resource "google_compute_region_disk_iam_policy" "compute_region_disk_access_control_test_policy" {
  project        = google_compute_region_disk.compute_region_disk_access_control_test.project
  region         = google_compute_region_disk.compute_region_disk_access_control_test.region
  name           = google_compute_region_disk.compute_region_disk_access_control_test.name
  policy_data    = data.google_iam_policy.compute_region_disk_access_control_test_iam_policy.policy_data
}
