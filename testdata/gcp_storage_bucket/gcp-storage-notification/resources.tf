provider "google-beta" {
  project = "None"
}

resource "google_storage_notification" "notification_sample" {
  provider = google-beta

  bucket = "bucket-svc"
  topic = "//pubsub.googleapis.com/projects/test/topics/test-file-upload"
  event_types = [
    "OBJECT_FINALIZE"
  ]
  payload_format = "JSON_API_V1"
}

#tfimport-terraform import google_storage_bucket.bucket_svc_resource  __project__/bucket-svc-resource
resource "google_storage_bucket" "bucket_svc_resource" {
  provider = google-beta

  name = "bucket-svc-resource"
  location = "US"
  versioning {
    enabled = false
  }
}
