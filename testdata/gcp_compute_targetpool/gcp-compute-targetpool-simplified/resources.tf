provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_compute_network.compute_network  __project__/compute-network
resource "google_compute_network" "compute_network" {
  provider = google-beta

  name = "compute-network"
  auto_create_subnetworks = false
}

#tfimport-terraform import google_compute_subnetwork.compute_subnetwork __project__/us-west1/compute-subnetwork
resource "google_compute_subnetwork" "compute_subnetwork" {
  provider = google-beta

  name = "compute-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region = "us-west1"
  network = google_compute_network.compute_network.id

  depends_on = [
    google_compute_network.compute_network
  ]
}

#tfimport-terraform import google_compute_instance_template.compute_instancetemplate  __project__/compute-instancetemplate
resource "google_compute_instance_template" "compute_instancetemplate" {
  provider = google-beta

  machine_type = "n1-standard-1"
  labels = {
    label-one = "value-one"
  }
  network_interface {
    network = google_compute_network.compute_network.id
    subnetwork = google_compute_subnetwork.compute_subnetwork.id
  }
  disk {
    auto_delete = false
    boot = true
    interface = "SCSI"
    source_image = "projects/debian-cloud/global/images/family/debian-11"
    disk_type = "pd-standard"
    labels = {
      label-one = "value-one"
    }
  }
  scheduling {
    on_host_maintenance = "MIGRATE"
    automatic_restart = true
    preemptible = false
  }

  depends_on = [
    google_compute_network.compute_network,
    google_compute_subnetwork.compute_subnetwork
  ]
}

resource "google_compute_instance_from_template" "compute_instance_1" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "compute-instance-1"
  zone = "us-west1-a"
  source_instance_template = google_compute_instance_template.compute_instancetemplate.id

  depends_on = [
    google_compute_instance_template.compute_instancetemplate
  ]
}

resource "google_compute_instance_from_template" "compute_instance_2" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "compute-instance-2"
  zone = "us-west1-b"
  source_instance_template = google_compute_instance_template.compute_instancetemplate.id

  depends_on = [
    google_compute_instance_template.compute_instancetemplate
  ]
}

#tfimport-terraform import google_compute_target_pool.compute_targetpool_1 __project__/us-west1/compute-targetpool-1
resource "google_compute_target_pool" "compute_targetpool_1" {
  provider = google-beta

  name = "compute-targetpool-1"
  region = "us-west1"
  instances = [
    "us-west1-a/compute-instance-1",
    "us-west1-b/compute-instance-2"
  ]
}

resource "google_compute_instance_from_template" "compute_instance_3" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "compute-instance-3"
  zone = "us-west1-a"
  source_instance_template = google_compute_instance_template.compute_instancetemplate.id

  depends_on = [
    google_compute_instance_template.compute_instancetemplate
  ]
}

resource "google_compute_instance_from_template" "compute_instance_4" {
  provider = google-beta

  labels = {
    label-one = "value-one"
  }
  name = "compute-instance-4"
  zone = "us-west1-b"
  source_instance_template = google_compute_instance_template.compute_instancetemplate.id

  depends_on = [
    google_compute_instance_template.compute_instancetemplate
  ]
}

#tfimport-terraform import google_compute_target_pool.compute_targetpool_2 __project__/us-west1/compute-targetpool-2
resource "google_compute_target_pool" "compute_targetpool_2" {
  provider = google-beta

  name = "compute-targetpool-2"
  description = "A pool of compute instances to use as a backend to a load balancer, with health check and backup pool. A hash of requester's IP is used to determine session affinity to instances."
  region = "us-west1"
  health_checks = [
    "compute-httphealthcheck-1"
  ]
  instances = [
    "us-west1-a/compute-instance-3",
    "us-west1-b/compute-instance-4"
  ]
  session_affinity = "CLIENT_IP"
  failover_ratio = 0.5
  backup_pool = google_compute_target_pool.compute_targetpool_1.id
}
