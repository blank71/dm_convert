provider "google-beta" {
  project = "None"
}

resource "google_monitoring_alert_policy" "monitoring_instance_uptime_check" {
  provider = google-beta

  display_name = "rax-mgcp-monitoring-instance-uptime-check"
  combiner = "OR"
  enabled = true
  notification_channels = [
    "projects/my-project/notificationChannels/123321"
  ]
  user_labels = {
    foo = "bar"
    label1 = "value1"
  }
  documentation {
    content = <<-EOT
    1. Ensure instance is responding.
       1. See GCE Instance Connectivity for connectivity instructions.
          - NOTE: Restart stackdriver monitoring agent if instance is accessible but alert is showing absent uptime metric.
    1. If no response, restart instance.
       1. `gcloud --project my-project compute instances reset $${INSTANCE}`
    1. If unable to diagnosis issue or resolve errors, call customer escalation list

    EOT
    mime_type = "text/markdown"
  }
  conditions {
    condition_threshold {
      filter = <<-EOT
metric.type="compute.googleapis.com/instance/uptime" AND
metadata.user_labels.autoscaled="false" AND
metadata.user_labels.monitored="true" AND
resource.type="gce_instance"

EOT
      comparison = "COMPARISON_LT"
      threshold_value = 1
      duration = "900s"
      trigger {
        count = 1
      }
      aggregations {
        alignment_period = "60s"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields = ["resource.label.instance_id"]
        per_series_aligner = "ALIGN_RATE"
      }
    }
    display_name = "Uptime check for GCE INSTANCE - Platform"
  }
}
