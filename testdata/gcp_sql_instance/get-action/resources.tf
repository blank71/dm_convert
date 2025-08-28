provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_pubsub_topic.pubsub_topic_resource  __project__/pubsub-topic
resource "google_pubsub_topic" "pubsub_topic_resource" {
  provider = google-beta

  labels = {
    sql-instance-name = data.google_sql_database_instance.get_sql_instance_action.master_instance_name
  }
  name = "pubsub-topic"
}

#tfimport-terraform import google_pubsub_topic.pubsub_resource_for_testing_depends_on  __project__/some-topic
resource "google_pubsub_topic" "pubsub_resource_for_testing_depends_on" {
  provider = google-beta

  name = "some-topic"
}

data "google_sql_database_instance" "get_sql_instance_action" {
  project = "test-project"
  name = "test-sql-instance"

  depends_on = [
    google_pubsub_topic.pubsub_resource_for_testing_depends_on
  ]
}
