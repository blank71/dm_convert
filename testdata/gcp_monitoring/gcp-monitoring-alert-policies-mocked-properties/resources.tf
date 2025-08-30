provider "google-beta" {
  project = "None"
}

resource "google_monitoring_alert_policy" "monitoring_instance_uptime_check" {
  provider = google-beta

  display_name = "test-monitoring-instance-uptime-check"
  combiner = "OR"
  enabled = true
  notification_channels = [
    "projects/my-project/notificationChannels/123321",
    "projects/my-project/notificationChannels/111111"
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
       1. `gcloud --project my-project compute instances reset INSTANCE`
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
      denominator_filter = <<-EOT
metric.type="compute.googleapis.com/instance/downtime"

EOT
      comparison = "COMPARISON_LT"
      threshold_value = 1
      duration = "900s"
      trigger {
        count = 1
        percent = 80
      }
      denominator_aggregations {
        alignment_period = "180s"
        cross_series_reducer = "REDUCE_NONE"
        group_by_fields = ["resource.label.instance_id", "resource.label.user_id"]
        per_series_aligner = "ALIGN_NONE"
      }
      denominator_aggregations {
        alignment_period = "10s"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields = ["resource.label.a2.instance_id", "resource.label.a2.user_id"]
        per_series_aligner = "ALIGN_DELTA"
      }
      aggregations {
        alignment_period = "60s"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields = ["resource.label.instance_id"]
        per_series_aligner = "ALIGN_RATE"
      }
    }
    display_name = "condition-Threshold"
  }
  conditions {
    condition_absent {
      filter = <<-EOT
resource.type="gce_instance"

EOT
      duration = "900s"
      trigger {
        count = 100
        percent = 3
      }
      aggregations {
        alignment_period = "180s"
        cross_series_reducer = "REDUCE_NONE"
        group_by_fields = ["resource.label.instance_id", "resource.label.user_id"]
        per_series_aligner = "ALIGN_NONE"
      }
      aggregations {
        alignment_period = "10s"
        cross_series_reducer = "REDUCE_MIN"
        group_by_fields = ["resource.label.absent1.instance_id", "resource.label.absent1.user_id"]
        per_series_aligner = "ALIGN_RATE"
      }
    }
    display_name = "condition-Absent"
  }
  conditions {
    condition_monitoring_query_language {
      query = <<-EOT
SELECT * FROM tmp WHERE a > b

EOT
      duration = "15s"
      trigger {
        count = 5
        percent = 15
      }
    }
    display_name = "condition-Query"
  }
}
#tfimport-PROJECT_ID="my-project"
#tfimport-FILE="${PROJECT_ID}.json"
#tfimport-DISPLAY_NAME="monitoring-instance-uptime-check"
#tfimport-if [[ ! -f "${FILE}" ]]; then gcloud alpha monitoring policies list --project="${PROJECT_ID}" --format=json > "${FILE}"; fi
#tfimport-ID=$(cat "${FILE}" | jq -r --arg display_name "${DISPLAY_NAME}" '.[] | select(.displayName == $display_name) | .name' )
#tfimport-terraform import google_monitoring_alert_policy.monitoring_instance_uptime_check ${ID}
