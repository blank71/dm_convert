provider "google-beta" {
  project = "None"
}

resource "google_cloudbuild_trigger" "cloud_buildtrigger" {
  provider = google-beta

  
  name = "cloud-buildtrigger"
  description = "Cloud Build Trigger for building the master branch of the GitHub repository at github.com/owner_name/repo_name"
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
  github {
    owner = "trodge"
    name = "cloud-foundation-toolkit"
    push {
      branch = "master"
    }
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
        "build",
        "-t",
        "gcr.io/$PROJECT_ID/${_SERVICE_NAME}:$COMMIT_SHA",
        "-f",
        "Dockerfile",
        "."
      ]
      id = "build_docker_image"
      timeout = google_cloudbuild_trigger.cloud_buildtrigger.timeout
    }
  }
}
#tfimport-terraform import google_cloudbuild_trigger.cloud_buildtrigger projects/__project__/locations/global/triggers/cloud-buildtrigger
