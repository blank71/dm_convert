provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_bigquery_dataset.bigquerydataset  tjr-dm-test-1/bigquerydataset
resource "google_bigquery_dataset" "bigquerydataset" {
  provider = google-beta

  default_table_expiration_ms = 3600000
  location = "us-west1"
  dataset_id = "bigquerydataset"
  project = "tjr-dm-test-1"
  access {
    role = "OWNER"
    user_by_email = "thomasrodgers@google.com"
  }
}

#tfimport-terraform import google_bigquery_table.bigquerytable  tjr-dm-test-1/bigquerydataset/bigquerytable
resource "google_bigquery_table" "bigquerytable" {
  provider = google-beta

  labels = {
    data-source = "external"
    schema-type = "auto-junk"
  }
  dataset_id = google_bigquery_dataset.bigquerydataset.dataset_id
  project = "tjr-dm-test-1"
  table_id = "bigquerytable"
  clustering = [
    "time_generated"
  ]
  time_partitioning {
    expiration_ms = 100
    field = "time_generated"
    type = "DAY"
  }
  range_partitioning {
    field = "created_by"
    range {
      start = 10
      end = 200
      interval = 20
    }
  }
  view {
    query = "SELECT * FROM view"
    use_legacy_sql = false
  }
  materialized_view {
    query = "SELECT * FROM materializedView"
    enable_refresh = true
    refresh_interval_ms = 1800000
  }
  schema = "[{\"mode\": \"NULLABLE\", \"name\": \"name\", \"type\": \"STRING\"}, {\"mode\": \"NULLABLE\", \"name\": \"date\", \"type\": \"DATE\"}]"
  external_data_configuration {
    source_uris = [
      "https://docs.google.com/spreadsheets/d/123456789012345",
      "https://docs.google.com/spreadsheets/d/abc"
    ]
    source_format = "GOOGLE_SHEETS"
    max_bad_records = 10
    autodetect = true
    ignore_unknown_values = true
    compression = "GZIP"
    csv_options {
      field_delimiter = ","
      skip_leading_rows = 123
      quote = ""
      allow_quoted_newlines = true
      allow_jagged_rows = true
      encoding = "UTF-8"
    }
    google_sheets_options {
      range = "sheet1!A1:B20"
      skip_leading_rows = 100
    }
    hive_partitioning_options {
      mode = "CUSTOM"
      source_uri_prefix = "gs://bucket/path_to_table/{dt:DATE}/{country:STRING}/{id:INTEGER}"
      require_partition_filter = false
    }
  }
  encryption_configuration {
    kms_key_name = google_kms_crypto_key.kms_crypto_key.name
  }

  depends_on = [
    google_bigquery_dataset.bigquerydataset
  ]
}

#tfimport-terraform import google_bigquery_dataset.test_deploymentdataset_test  __project__/test_deploymentdataset
resource "google_bigquery_dataset" "test_deploymentdataset_test" {
  provider = google-beta

  dataset_id = "test_deploymentdataset"
}

#tfimport-terraform import google_bigquery_table.test_deploymenttable_test  __project__/test_deploymentdataset/test_deploymenttable
resource "google_bigquery_table" "test_deploymenttable_test" {
  provider = google-beta

  dataset_id = google_bigquery_dataset.test_deploymentdataset_test.dataset_id
  expiration_time = 1700000000000
  table_id = "test_deploymenttable"
  schema = "[{\"mode\": \"NULLABLE\", \"name\": \"name\", \"type\": \"STRING\"}, {\"mode\": \"NULLABLE\", \"name\": \"date\", \"type\": \"DATE\"}]"
  external_data_configuration {
    autodetect = false
    source_uris = [
      "https://docs.google.com/spreadsheets/d/123456789012345",
      "https://docs.google.com/spreadsheets/d/abc"
    ]
    source_format = "GOOGLE_SHEETS"
    avro_options {
      use_avro_logical_types = true
    }
  }

  depends_on = [
    google_bigquery_dataset.test_deploymentdataset_test
  ]
}

#tfimport-terraform import google_bigquery_dataset.test_deploymentdataset_test_1  __project__/test_deploymentdataset_1
resource "google_bigquery_dataset" "test_deploymentdataset_test_1" {
  provider = google-beta

  dataset_id = "test_deploymentdataset_1"
}

#tfimport-terraform import google_bigquery_table.test_deploymenttable_test_1  __project__/test_deploymentdataset_1/test_deploymenttable-1
resource "google_bigquery_table" "test_deploymenttable_test_1" {
  provider = google-beta

  dataset_id = google_bigquery_dataset.test_deploymentdataset_test_1.dataset_id
  table_id = "test_deploymenttable-1"
  encryption_configuration {
    kms_key_name = google_kms_crypto_key.kms_crypto_key.name
  }

  depends_on = [
    google_bigquery_dataset.test_deploymentdataset_test_1,
    google_kms_crypto_key.kms_crypto_key
  ]
}

#tfimport-terraform import google_kms_crypto_key.kms_crypto_key kms-key-ring/kms-crypto-key
resource "google_kms_crypto_key" "kms_crypto_key" {
  provider = google-beta

  name = "kms-crypto-key"
  purpose = "ENCRYPT_DECRYPT"
  key_ring = google_kms_key_ring.kms_key_ring.id

  depends_on = [
    google_kms_key_ring.kms_key_ring
  ]
}

resource "google_kms_key_ring" "kms_key_ring" {
  provider = google-beta

  name = "kms-key-ring"
  location = "global"
}
#tfimport-terraform import google_kms_key_ring.kms_key_ring __project__/global/kms-key-ring
