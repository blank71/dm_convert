provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project.rm_project  rm-project
resource "google_project" "rm_project" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "Project in Org"
  project_id = "rm-project"
  org_id = "128653134652"
}
