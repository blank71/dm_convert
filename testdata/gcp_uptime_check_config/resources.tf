provider "google-beta" {
  project = "None"
}

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
#tfimport-PROJECT_ID="__project__"
#tfimport-FILE="${PROJECT_ID}_monitoring_uptime_check_config.json"
#tfimport-DISPLAY_NAME="My uptime check config"
#tfimport-if [[ ! -f "${FILE}" ]]; then gcloud monitoring uptime list-configs --project="${PROJECT_ID}" --format="json(displayName,name)" > "${FILE}"; fi
#tfimport-ID=$(cat "${FILE}" | jq -r --arg display_name "${DISPLAY_NAME}" '.[] | select(.displayName == $display_name) | .name' )
#tfimport-terraform import google_monitoring_uptime_check_config.my_uptime_check_config ${ID}
