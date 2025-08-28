provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_global_forwarding_rule.https_global_forwarding_resource  __project__/my-forwarding-rule
resource "google_compute_global_forwarding_rule" "https_global_forwarding_resource" {
  provider = google-beta

  name = "my-forwarding-rule"
  ip_address = "192.168.0.1"
  ip_protocol = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range = "443-443"
  target = "my-https-target-proxy"
}
