locals {
  # To use wif with Gitlab / Github, please fill in the following local values
  # and contribute them back to Nimbus.
  attribute_condition = ""
  audiences           = [""]
  issuer_uri          = ""
}

module "wif" {
  source                  = "../modules/wif"
  project                 = var.project
  attribute_condition     = local.attribute_condition
  audiences               = local.audiences
  issuer_uri              = local.issuer_uri
  cicd_service_account_id = "svc-cicd"
  svc_cicd_roles = [
    "roles/storage.admin",
    "roles/cloudbuild.builds.editor"
  ]
}

resource "google_project_service" "iam_credentials" {
  project = var.project
  service = "iamcredentials.googleapis.com"
}

resource "google_project_service" "iam" {
  project    = var.project
  service    = "iam.googleapis.com"
  depends_on = [google_project_service.iam_credentials]
}

resource "google_project_service" "cloud_resource_manager" {
  project = var.project
  service = "cloudresourcemanager.googleapis.com"
}

resource "google_project_service" "sts" {
  project = var.project
  service = "sts.googleapis.com"
}
