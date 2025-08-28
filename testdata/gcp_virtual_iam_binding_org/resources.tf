provider "google-beta" {
  project = "None"
}

resource "google_organization_iam_member" "virtual_iam_member_binding_org" {
  provider = google-beta

  role = "roles/artifactregistry.admin"
  member = "user:user1@google.com"
  org_id = "12345678"
}
#tfimport-terraform import google_organization_iam_member.virtual_iam_member_binding_org  "12345678 roles/artifactregistry.admin user:user1@google.com"
