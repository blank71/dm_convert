provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.fake_network  __project__/fake-network
resource "google_compute_network" "fake_network" {
  provider = google-beta

  name = "fake-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork_access_control_test __project__/us-west1/compute-subnetwork-access-control-test
resource "google_compute_subnetwork" "compute_subnetwork_access_control_test" {
  provider = google-beta

  name = "compute-subnetwork-access-control-test"
  description = "Test subnet"
  ip_cidr_range = "192.168.0.0/24"
  region = "us-west1"
  network = google_compute_network.fake_network.id
}

data "google_iam_policy" "compute_subnetwork_access_control_test_iam_policy" {
  binding {
    role = "roles/compute.instanceAdminV1"
    members = [
      "user:user1@google.com",
      "user:user2@google.com",
    ]
  }
  binding {
    role = "roles/compute.networkViewer"
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

#tfimport-terraform import google_compute_subnetwork_iam_policy.compute_subnetwork_access_control_test_policy __project__/us-west1/compute-subnetwork-access-control-test
resource "google_compute_subnetwork_iam_policy" "compute_subnetwork_access_control_test_policy" {
  project        = google_compute_subnetwork.compute_subnetwork_access_control_test.project
  region         = google_compute_subnetwork.compute_subnetwork_access_control_test.region
  subnetwork     = google_compute_subnetwork.compute_subnetwork_access_control_test.name
  policy_data    = data.google_iam_policy.compute_subnetwork_access_control_test_iam_policy.policy_data
}
