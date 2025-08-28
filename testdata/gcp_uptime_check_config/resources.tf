provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_monitoring_uptime_check_config.my_uptime_check_config  __project__//my-uptime-check-config
resource "google_monitoring_uptime_check_config" "my_uptime_check_config" {
  provider = google-beta

  display_name = "My uptime check config"
  timeout = "10s"
  content_matchers{
    content = "example"
    matcher = "CONTAINS_STRING"
  }
  http_check{
    path = "/"
    port = "80"
    request_method = "POST"
    content_type = "USER_PROVIDED"
    custom_content_type = "application/json"
    body = "Zm9vJTI1M0RiYXI="
    ping_config {
      pings_count = "1"
    }
  }
  monitored_resource {
    type = "uptime_url"
    labels = {
      "url": "https://www.google.com/",
    }
  }
}
