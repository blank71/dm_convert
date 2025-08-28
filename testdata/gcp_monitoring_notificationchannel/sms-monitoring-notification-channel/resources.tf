provider "google-beta" {
  project = "None"
}

resource "google_monitoring_notification_channel" "monitoring_notificationchannel" {
  provider = google-beta

  labels = {
    number = "12025550196"
  }
  user_labels = {
    response-priority = "intervention"
    target-user = "on-call"
  }
  type = "sms"
  display_name = "monitoring-notificationchannel"
  description = "A channel that sends notifications via Short Message Service (SMS)."
  enabled = true
}
