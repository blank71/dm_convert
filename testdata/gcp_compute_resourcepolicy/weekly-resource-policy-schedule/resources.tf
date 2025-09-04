provider "google-beta" {
  project = "None"
}

resource "google_compute_resource_policy" "compute_resource_policy" {
  provider = google-beta

  name = "compute-resource-policy"
  region = "us-central1"
  snapshot_schedule_policy {
    retention_policy {
      max_retention_days = 12
    }
    schedule {
      weekly_schedule {
        day_of_weeks {
          day = "MONDAY"
          start_time = "08:00"
        }
        day_of_weeks {
          day = "WEDNESDAY"
          start_time = "15:00"
        }
        day_of_weeks {
          day = "FRIDAY"
          start_time = "23:00"
        }
      }
    }
    snapshot_properties {
      storage_locations = [
        "us"
      ]
      labels = {
        autodeleted = "false"
        interval = "weekly"
      }
    }
  }
}
#tfimport-terraform import google_compute_resource_policy.compute_resource_policy projects/__project__/regions/us-central1/resourcePolicies/compute-resource-policy
