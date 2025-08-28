provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_access_context_manager_service_perimeter_resource.service_perimeter_resource  __project__//service-perimeter-resource
resource "google_access_context_manager_service_perimeter_resource" "service_perimeter_resource" {
  provider = google-beta

  perimeter_name = "google_access_context_manager_service_perimeter.service-perimeter-resource.name"
  resource = "projects/987654321"
}
