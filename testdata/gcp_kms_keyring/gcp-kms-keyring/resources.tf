provider "google-beta" {
  project = "None"
}

resource "google_kms_key_ring" "kms_keyring" {
  provider = google-beta

  name = "kms-keyring"
  location = "us-central1"
}
#tfimport-terraform import google_kms_key_ring.kms_keyring __project__/us-central1/kms-keyring
