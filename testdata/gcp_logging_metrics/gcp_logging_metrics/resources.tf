provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_logging_metric.my_metric __project__ my_metric
resource "google_logging_metric" "my_metric" {
  provider = google-beta

  name = "my_metric"
  filter = "resource.type=\"gce_instance\" logName=\"projects/my-project/logs/my-logs\" jsonPayload.message:\"Registering job\""
  description = "Captures data when smoke test was registered"
  metric_descriptor {
    metric_kind = "DELTA"
    value_type = "INT64"
    unit = "1"
    display_name = "camelCase"
    labels {
      key = "instance_name"
      value_type = "STRING"
    }
    labels {
      key = "project_name"
      value_type = "STRING"
    }
  }
  bucket_options {
    linear_buckets {
      num_finite_buckets = 4
      width = 1
      offset = 2
    }
    exponential_buckets {
      num_finite_buckets = 4
      growth_factor = 1
      scale = 10
    }
    explicit_buckets {
      bounds = [1, 2, 3, 4]
    }
  }
  label_extractors = {
    "instance_name" = "EXTRACT(resource.labels.instance_id)"
    "project_name" = "EXTRACT(resource.labels.project_id)"
  }
}
