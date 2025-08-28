provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_folder.rm_folder rm_folder
resource "google_folder" "rm_folder" {
  provider = google-beta

  display_name = "rm-folder"
  parent = "organizations/128653134652"
}
