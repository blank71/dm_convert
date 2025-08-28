provider "google-beta" {
  project = "None"
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.settings.backupConfiguration.replicationLogArchivingEnabled: False
#
#tfimport-terraform import google_sql_database_instance.sql_instance  __project__/sql-instance
resource "google_sql_database_instance" "sql_instance" {
  provider = google-beta

  name = "sql-instance"
  database_version = "POSTGRES_9_6"
  region = "us-central1"
  settings {
    tier = "db-custom-1-3840"
    availability_type = "REGIONAL"
    location_preference {
      zone = "us-central1-a"
    }
    backup_configuration {
      binary_log_enabled = false
      point_in_time_recovery_enabled = false
    }
    ip_configuration {
      ipv4_enabled = true
    }

  }
}
