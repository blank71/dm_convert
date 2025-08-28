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
  database_version = "MYSQL_5_7"
  region = "us-central1"
  settings {
    tier = "db-n1-standard-1"
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

#tfimport-terraform import google_sql_database.sql_database  __project__/sql-instance/sql-database
resource "google_sql_database" "sql_database" {
  provider = google-beta

  name = "sql-database"
  instance = "sql-instance"
  charset = "utf8mb4"
  collation = "utf8mb4_bin"
  project = "test-project-id"
}

#tfimport-terraform import google_sql_database.sql_database_1  __project__/sql-instance/sql-database-1
resource "google_sql_database" "sql_database_1" {
  provider = google-beta

  name = "sql-database-1"
  instance = "sql-instance"
  charset = "utf8mb4"
}
