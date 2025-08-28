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

#tfimport-terraform import google_sql_user.sql_user  __project__/sql-instance/%/sql-user
resource "google_sql_user" "sql_user" {
  provider = google-beta

  name = "sql-user"
  instance = "sql-instance"
  host = "%"
  password = "cGFzc3dvcmQ="
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.settings.backupConfiguration.replicationLogArchivingEnabled: False
#
#tfimport-terraform import google_sql_database_instance.sql_instance_1  __project__/sql-instance-1
resource "google_sql_database_instance" "sql_instance_1" {
  provider = google-beta

  name = "sql-instance-1"
  database_version = "MYSQL_8_0_31"
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

#tfimport-terraform import google_sql_user.sql_user_1  __project__/sql-instance-1/%/sql-user-1
resource "google_sql_user" "sql_user_1" {
  provider = google-beta

  name = "sql-user-1"
  instance = "sql-instance-1"
  host = "%"
  password = "cGFzc3dvcmQ="
  project = "test-project-id"
  type = "BUILT_IN"
  password_policy {
    allowed_failed_attempts = 10
    password_expiration_duration = "86400s"
    enable_failed_attempts_check = false
    enable_password_verification = false
  }
}

#tfimport-terraform import google_sql_user.sql_user_2  __project__/sql-instance/%/sql-user-2
resource "google_sql_user" "sql_user_2" {
  provider = google-beta

  name = "sql-user-2"
  instance = "sql-instance"
  host = "%"
  password = "cGFzc3dvcmQ="
}
