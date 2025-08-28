provider "google-beta" {
  project = "None"
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.settings.backupConfiguration.replicationLogArchivingEnabled: False
#
#tfimport-terraform import google_sql_database_instance.sql_instance_1  __project__/sql-instance-1
resource "google_sql_database_instance" "sql_instance_1" {
  provider = google-beta

  name = "sql-instance-1"
  database_version = "MYSQL_5_7"
  region = "us-central1"
  settings {
    tier = "db-f1-micro"
    location_preference {
      zone = "us-central1-b"
    }
    backup_configuration {
      binary_log_enabled = true
      enabled = true
      point_in_time_recovery_enabled = false
      start_time = "18:00"
    }
    ip_configuration {
      ipv4_enabled = true
    }

  }
}

#tfimport-terraform import google_sql_database_instance.sql_instance_2  __project__/sql-instance-2
resource "google_sql_database_instance" "sql_instance_2" {
  provider = google-beta

  name = "sql-instance-2"
  database_version = "MYSQL_5_7"
  region = "us-central1"
  master_instance_name = "sql-instance-1"
  settings {
    tier = "db-f1-micro"
    location_preference {
      zone = "us-central1-c"
    }
    backup_configuration {
      binary_log_enabled = false
    }
    ip_configuration {
      ipv4_enabled = true
    }

  }
  replica_configuration{
    connect_retry_interval = 30
  }
}
