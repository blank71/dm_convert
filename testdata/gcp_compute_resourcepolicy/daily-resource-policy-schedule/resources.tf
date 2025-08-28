provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_resource_policy.compute_resource_policy  __project__/us-central1/compute-resource-policy
resource "google_compute_resource_policy" "compute_resource_policy" {
  provider = google-beta

  name = "compute-resource-policy"
  description = "this is description field"
  region = "us-central1"
  snapshot_schedule_policy {
    retention_policy {
      max_retention_days = 8
      on_source_disk_delete = "KEEP_AUTO_SNAPSHOTS"
    }
    schedule {
      daily_schedule {
        days_in_cycle = 1
        start_time = "00:00"
      }
    }
    snapshot_properties {
      storage_locations = [
        "us-central1"
      ]
      guest_flush = true
      labels = {
        autodeleted = "false"
        interval = "daily"
      }
    }
  }
}
