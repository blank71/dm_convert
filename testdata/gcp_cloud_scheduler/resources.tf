provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_cloud_scheduler_job.scheduler_job  __project__//scheduler-job
resource "google_cloud_scheduler_job" "scheduler_job" {
  provider = google-beta

  name = "scheduler-job"
  description = "My dummy scheduler job"
  time_zone = "America/Los_Angeles"
  schedule = "0 * * * *"
  http_target {
    uri = "https://my-service.example.com"
    http_method = "POST"
    body = base64encode("{\"foo\":\"bar\"}")
  }
}
