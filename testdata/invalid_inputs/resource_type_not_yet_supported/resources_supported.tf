provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_storage_bucket.resource_type_supported  __project__/resource-type-supported
resource "google_storage_bucket" "resource_type_supported" {
  provider = google-beta

  name = "resource-type-supported"
  location = "US"
  storage_class = "STANDARD"
}
