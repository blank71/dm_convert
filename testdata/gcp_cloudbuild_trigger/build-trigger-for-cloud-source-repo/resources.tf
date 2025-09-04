provider "google-beta" {
  project = "None"
}

resource "google_cloudbuild_trigger" "cloud_buildtrigger" {
  provider = google-beta

  
  name = "cloud-buildtrigger"
  description = "Cloud Build Trigger for building the master branch of the referenced Cloud Source Repository."
  disabled = false
  ignored_files = [
    "**/*.md"
  ]
  included_files = [
    "src/**"
  ]
  substitutions = {
    _SERVICE_NAME = "service-name"
  }
  trigger_template {
    repo_name = "projects/tjr-dm-test-1/repos/sourcerepo-repo"
    branch_name = "master"
    dir = "team-a/service-b"
  }
  build {
    images = [
      "gcr.io/$PROJECT_ID/${_SERVICE_NAME}:$COMMIT_SHA"
    ]
    tags = [
      "team-a",
      "service-b"
    ]
    timeout = "1800s"
    step {
      name = "gcr.io/cloud-builders/gsutil"
      args = [
        "cp",
        "gs://mybucket/remotefile.zip",
        "localfile.zip"
      ]
      id = "download_zip"
      timeout = "120s"
    }
    step {
      name = "gcr.io/cloud-builders/go"
      args = [
        "build",
        "my_package"
      ]
      env = [
        "ENV1=one",
        "ENV2=two"
      ]
      dir = "directory"
      id = "build_package"
      secret_env = [
        "SECRET_ENV1"
      ]
      timeout = "120s"
    }
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        google_cloudbuild_trigger.cloud_buildtrigger.args_0_,
        "-t",
        "gcr.io/$PROJECT_ID/${_SERVICE_NAME}:$COMMIT_SHA",
        "-f",
        "Dockerfile",
        "."
      ]
      id = "build_docker_image"
      timeout = "120s"
    }
  }
}
#tfimport-terraform import google_cloudbuild_trigger.cloud_buildtrigger projects/__project__/locations/global/triggers/cloud-buildtrigger
