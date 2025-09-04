provider "google-beta" {
  project = "None"
}

resource "google_compute_network" "fake_network" {
  provider = google-beta

  name = "fake-network"
  auto_create_subnetworks = false
  routing_mode = "REGIONAL"
}
#tfimport-terraform import google_compute_network.fake_network  projects/__project__/global/networks/fake-network

resource "google_compute_subnetwork" "compute_subnetwork_access_control_test" {
  provider = google-beta

  name = "compute-subnetwork-access-control-test"
  description = "Test subnet"
  ip_cidr_range = "192.168.0.0/24"
  region = "us-west1"
  network = google_compute_network.fake_network.id
}
#tfimport-terraform import google_compute_subnetwork.compute_subnetwork_access_control_test projects/__project__/regions/us-west1/subnetworks/compute-subnetwork-access-control-test

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

#tfimport-terraform import google_compute_subnetwork_iam_policy.compute_subnetwork_access_control_test_policy projects/__project__/regions/us-west1/subnetworks/compute-subnetwork-access-control-test
resource "google_compute_subnetwork_iam_policy" "compute_subnetwork_access_control_test_policy" {
  project        = google_compute_subnetwork.compute_subnetwork_access_control_test.project
  region         = google_compute_subnetwork.compute_subnetwork_access_control_test.region
  subnetwork     = google_compute_subnetwork.compute_subnetwork_access_control_test.name
  policy_data    = data.google_iam_policy.compute_subnetwork_access_control_test_iam_policy.policy_data
}
