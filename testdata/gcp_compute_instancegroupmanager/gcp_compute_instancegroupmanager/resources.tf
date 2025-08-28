provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_instance_group_manager.it_global  __project__/europe-west4-a/it-global
resource "google_compute_instance_group_manager" "it_global" {
  provider = google-beta

  base_instance_name = "it"
  target_size = 1
  zone = "europe-west4-a"
  name = "it-global"
  version {
    instance_template = "projects/my-project/global/instanceTemplates/it-global"
  }
  named_port {
    name = "front"
    port = 443
  }
  auto_healing_policies {
    health_check = "fake-health-check-self-link-here"
    initial_delay_sec = 900
  }
  update_policy {
    type = "PROACTIVE"
    minimal_action = "REPLACE"
    max_surge_percent = 1
    max_unavailable_fixed = 0
  }
  stateful_disk {
    device_name = "test-boot"
    delete_rule = "ON_PERMANENT_INSTANCE_DELETION"
  }
  stateful_disk {
    device_name = "test-data"
    delete_rule = "NEVER"
  }
}
