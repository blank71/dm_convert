provider "google-beta" {
  project = "None"
}

resource "google_kms_key_ring" "kms_keyring" {
  provider = google-beta

  name = "kms-keyring"
  location = "us-central1"
}
#tfimport-terraform import google_kms_key_ring.kms_keyring __project__/us-central1/kms-keyring

#tfimport-terraform import google_kms_crypto_key.kms_cryptokey kms-keyring/kms-cryptokey
resource "google_kms_crypto_key" "kms_cryptokey" {
  provider = google-beta

  labels = {
    key-one = "value-one"
  }
  name = "kms-cryptokey"
  purpose = "ASYMMETRIC_SIGN"
  key_ring = google_kms_key_ring.kms_keyring.id
  version_template {
    algorithm = "EC_SIGN_P384_SHA384"
    protection_level = "SOFTWARE"
  }

  depends_on = [
    google_kms_key_ring.kms_keyring
  ]
}
