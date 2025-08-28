provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_access_context_manager_access_policy.my_access_level  __project__//my-access-level
resource "google_access_context_manager_access_level_condition" "my_access_level" {
  provider = google-beta

  access_level = "google_access_context_manager_access_level.access-level-service-account.name"
  negate = false
  ip_subnetworks = [
    "192.0.4.0/24"
  ]
  members = [
    "user:test@google.com",
    "user:test2@google.com",
    "serviceAccount:sa-test@google.com"
  ]
  regions = [
    "IT",
    "US"
  ]
  device_policy {
    require_screen_lock = false
    require_admin_approval = false
    require_corp_owned = true
  }
}
