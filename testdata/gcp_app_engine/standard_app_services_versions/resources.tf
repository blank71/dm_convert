provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_app_engine_standard_app_version.magellan_gcs_uploader_v1 __project__/magellan-iot-filetypeiottest/magellan_gcs_uploader_v1
resource "google_app_engine_standard_app_version" "magellan_gcs_uploader_v1" {
  provider = google-beta

  runtime = "go"
  service = "magellan-iot-filetypeiottest"
  version_id = "magellan_gcs_uploader_v1"
  env_variables = {
    "BLOCKS_URL" = ""
    "STORAGE_BUCKET" = "ml-test-data"
  }
  deployment {
    files {
      name = "github.com/golang/protobuf/proto/clone.go"
      source_url = "https://storage.googleapis.com/magellan-gae-repository/magellan-gcs-uploader/v1/github.com/golang/protobuf/proto/clone.go"
      sha1_sum = "9a016945b0d1350e607f5bba666c26d6244eb074"
    }
  }
  handlers {
    url_regex = "/.*"
    script {
      script_path = "_go_app"
    }
  }
  entrypoint {
    shell = "go run myapp"
  }
}
