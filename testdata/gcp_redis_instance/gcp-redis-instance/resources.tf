provider "google-beta" {
  project = "None"
}

resource "google_redis_instance" "redis_instance" {
  provider = google-beta

  name = "redis-instance"
  tier = "BASIC"
  memory_size_gb = 16
  labels = {
    label-one = "value-one"
  }
  
  display_name = "Sample Redis Instance"
}
#tfimport-terraform import google_redis_instance.redis_instance  projects/tjr-dm-test-1/locations/us-central1/instances/redis-instance
