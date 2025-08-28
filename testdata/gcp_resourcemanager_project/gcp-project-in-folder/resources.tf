provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_project.rm_project  rm-project
resource "google_project" "rm_project" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "Project in Folder"
  project_id = "rm-project"
  folder_id = "328101438358"
}
