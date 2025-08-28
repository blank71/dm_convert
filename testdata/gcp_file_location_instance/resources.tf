provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_filestore_instance.filestore______  __project__//filestore-{{.}}
resource "google_filestore_instance" "filestore______" {
  provider = google-beta

  labels = {
    dg_data_confidentiality = "need_to_know"
    dg_data_context = "metadata"
    dg_data_source = "end_user"
  }
  name = "filestore-{{.}}"
  tier = "STANDARD"
  networks {
    network = "default"
    modes = [
      "MODE_IPV4"
    ]
  }
  file_shares {
    name = "data"
    capacity_gb = 1024
  }
}
