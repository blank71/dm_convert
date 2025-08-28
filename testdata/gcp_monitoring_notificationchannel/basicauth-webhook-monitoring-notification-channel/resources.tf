provider "google-beta" {
  project = "None"
}

resource "google_monitoring_notification_channel" "monitoring_notificationchannel" {
  provider = google-beta

  labels = {
    password = "cGFzc3dvcmQK"
    url = "http://hooks.example.com/notifications"
    username = "admin"
  }
  user_labels = {
    response-priority = "all"
    target-user = "automation"
  }
  type = "webhook_basicauth"
  display_name = "monitoring-notificationchannel"
  description = "Sends notifications to indicated webhook URL using HTTP-standard basic authentication. Should be used in conjunction with SSL/TLS to reduce the risk of attackers snooping the credentials."
}
