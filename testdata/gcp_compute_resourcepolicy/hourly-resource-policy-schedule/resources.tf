provider "google-beta" {
  project = "None"
}

resource "google_compute_resource_policy" "compute_resource_policy" {
  provider = google-beta

  name = "compute-resource-policy"
  region = "us-central1"
  snapshot_schedule_policy {
    retention_policy {
      max_retention_days = 2
      on_source_disk_delete = "APPLY_RETENTION_POLICY"
    }
    schedule {
      hourly_schedule {
        hours_in_cycle = 4
        start_time = "13:00"
      }
    }
    snapshot_properties {
      labels = {
        autodeleted = "true"
        interval = "hourly"
      }
    }
  }
}
#tfimport-terraform import google_compute_resource_policy.compute_resource_policy projects/__project__/regions/us-central1/resourcePolicies/compute-resource-policy
