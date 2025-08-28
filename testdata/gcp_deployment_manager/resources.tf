provider "google-beta" {
  project = "None"
}

#tfimport-terraform import google_deployment_manager_deployment.prober_list_types  __project__//prober-list-types
resource "google_deployment_manager_deployment" "prober_list_types" {
  provider = google-beta

  name = "prober-list-types"
  target {
    config {
      content = <<-EOT
imports:
- all-types.jinja
resources:
- name: all-types
  type: all-types.jinja
  properties: $(ref.list-providers.toString())

EOT
    }
    imports {
      name = "all-types.jinja"
      content = <<-EOT
resources:
{% for type in properties["typeProviders"] %}
- name: type-list-{{ type.name }}
  action: gcp-types/deploymentmanager-v2beta:deploymentmanager.typeProviders.listTypes
  properties:
    project: gcp-types
    typeProvider: {{ type.name }}
    fields: types/name
{% endfor %}

EOT
    }
    }
}
