provider "google-beta" {
  project = "None"
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.state: RUNNABLE
# properties.settings.backupConfiguration.replicationLogArchivingEnabled: False
#
#tfimport-terraform import google_sql_database_instance.sql_instance  __project__/sql-instance
resource "google_sql_database_instance" "sql_instance" {
  provider = google-beta

  name = "sql-instance"
  database_version = "MYSQL_5_7"
  region = "us-central1"
  project = "test-project-id"
  root_password = "abcd"
  settings {
    tier = "db-f1-micro"
    disk_size = 10
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
    failover_target = true
    dump_file_path = "abc/123"
    username = "test-user"
    password = "test-pass"
    connect_retry_interval = 30
    master_heartbeat_period = 10
    ca_certificate = "abcdefgh"
    client_certificate = "abcdef"
    client_key = "abcd"
    ssl_cipher = "abc"
    verify_server_certificate = false
  }
}



# ----This file was created by Deployment Manager Convertor (DMC) Tool. This resource contains resource configuration fields that are not supported by Terraform. ---- #
# ---- Please review and update those fields as needed by DM Convert ---- #

# properties.settings.backupConfiguration.replicationLogArchivingEnabled: False
#
#tfimport-terraform import google_sql_database_instance.sql_instance_3  __project__/sql-instance-3
resource "google_sql_database_instance" "sql_instance_3" {
  provider = google-beta

  name = "sql-instance-3"
  database_version = "MYSQL_5_7"
  region = "us-central1"
  settings {
    tier = "db-f1-micro"
    disk_size = 10
    availability_type = "ZONAL"
    pricing_plan = "PER_USE"
    disk_autoresize_limit = 10
    activation_policy = "ALWAYS"
    disk_autoresize = true
    disk_type = "PD_SSD"
    edition = "ENTERPRISE"
    connector_enforcement = "NOT_REQUIRED"
    deletion_protection_enabled = false
    location_preference {
      zone = "us-central1-a"
      secondary_zone = "us-central1-b"
    }
    data_cache_config {
      data_cache_enabled = false
    }
    maintenance_window {
      day = 7
      hour = 12
      update_track = "stable"
    }
    backup_configuration {
      backup_retention_settings {
        retention_unit = "COUNT"
        retained_backups = 5
      }
      binary_log_enabled = false
      enabled = true
      location = "us-central1"
      point_in_time_recovery_enabled = false
      start_time = "18:00"
      transaction_log_retention_days = 5
    }
    database_flags {
      name = "max_allowed_packet"
      value = 16777216
    }
    ip_configuration {
      ipv4_enabled = true
      private_network = "projects/project-id/global/networks/default"
      allocated_ip_range = "IP_RANGE"
      authorized_networks {
        name = "postgres-ha-solution-cidr"
        value = "192.10.10.10/32"
        expiration_time = "2023-11-15T16:19:00.094Z"
      }
    }

    user_labels = {
      key1 = "value1"
      key2 = "value2"
    }
  }
}

#tfimport-terraform import google_sql_database_instance.sql_instance_4  __project__/sql-instance-4
resource "google_sql_database_instance" "sql_instance_4" {
  provider = google-beta

  name = "sql-instance-4"
  database_version = "MYSQL_5_7"
  region = "us-central1"
  settings {
    tier = "db-f1-micro"
    disk_size = 10

  }
}
