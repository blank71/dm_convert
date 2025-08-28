provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_instance_template.it_opt_binpacking_g2  __project__/it_opt-binpacking_g2
resource "google_compute_instance_template" "it_opt_binpacking_g2" {
  provider = google-beta

  name = "opt-binpacking-g2"
  tags = [
    "binpacking-optimize"
  ]
  machine_type = "n1-standard-4"
  can_ip_forward = false
  min_cpu_platform = "Intel Haswell"
  labels = {
    container-vm = "cos-stable"
  }
  metadata = {
    gce-container-declaration = <<-EOT
# DISCLAIMER:
# This container declaration format is not a public API and may change without
# notice. Please use gcloud command-line tool or Google Cloud Console to run
# Containers on Google Compute Engine.

spec:
  containers:
  - env:
    - name: REQUEST_SUBSCRIPTION
      value: subscription_opt-binpacking-request
    - name: RESPONSE_TOPIC
      value: projects/project-a/topics/opt-binpacking-result
    - name: HEAP_LIMIT_MB
      value: '14336'
    image: gcr.io/blocks-private-registry/gn-binpacking-optimizer:stable
    name: opt-binpacking
    securityContext:
      privileged: false
    stdin: false
    tty: false
    volumeMounts: []
  restartPolicy: OnFailure
  volumes: []

EOT
    google-logging-enabled = "true"
  }
  network_interface {
    network = "network_optimization"
    access_config {
    }
  }
  disk {
    auto_delete = true
    device_name = "persistent-disk-0"
    boot = true
    source_image = "projects/cos-cloud/global/images/family/cos-stable"
    labels = {
      container-vm = "cos-stable"
    }
  }
  service_account {
    email = "default"
    scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/"
    ]
  }
  scheduling {
    on_host_maintenance = "MIGRATE"
    automatic_restart = true
    preemptible = false
  }
  reservation_affinity {
    type = "ANY_RESERVATION"
    specific_reservation {
      key = "key-here"
      values = [
        "line1",
        "line2",
        "line3"
      ]
    }
  }
}
