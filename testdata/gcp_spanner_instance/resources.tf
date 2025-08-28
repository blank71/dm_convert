provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_spanner_instance.foo_id __project__/foo-id
resource "google_spanner_instance" "foo_id" {
  provider = google-beta

  name = "foo-id"
  display_name = "test with nodeCount"
  config = "regional-us-central1"
  num_nodes = "5"
  labels = {
    foo = "bar"
  }
}

#tfimport-terraform import google_spanner_instance.bar_id __project__/bar-id
resource "google_spanner_instance" "bar_id" {
  provider = google-beta

  name = "bar-id"
  display_name = "test with processing Units"
  config = "regional-us-central1"
  num_nodes = "5"
  labels = {
    foo = "bar"
  }
}
