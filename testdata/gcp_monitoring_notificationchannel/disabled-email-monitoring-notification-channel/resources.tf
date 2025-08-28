provider "google-beta" {
  project = "None"
}

resource "google_monitoring_notification_channel" "monitoring_notificationchannel" {
  provider = google-beta

  labels = {
    email_address = "dev@example.com"
  }
  user_labels = {
    response-priority = "longterm"
    target-user = "dev"
  }
  type = "email"
  display_name = "monitoring-notificationchannel"
  description = "A disabled channel that would send notifications via email if enabled."
  enabled = false
}
