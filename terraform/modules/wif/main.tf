resource "google_iam_workload_identity_pool" "cicd_identity_pool" {
  project                   = var.project
  provider                  = google-beta
  workload_identity_pool_id = "cicd-identity-pool"
  display_name              = "CI/CD Identity Pool"
  description               = "Identity pool for CI/CD pipelines"
}

resource "google_iam_workload_identity_pool_provider" "cicd_identity_provider" {
  project                            = var.project
  provider                           = google-beta
  workload_identity_pool_id          = google_iam_workload_identity_pool.cicd_identity_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "cicd-identity-provider"
  display_name                       = "CI/CD Provider"
  description                        = "OIDC identity pool provider for CI/CD pipelines"

  attribute_condition = var.attribute_condition
  attribute_mapping   = var.attribute_mapping

  oidc {
    allowed_audiences = var.audiences
    issuer_uri        = var.issuer_uri
  }
}

resource "google_service_account" "cicd_service_account" {
  account_id   = var.cicd_service_account_id
  display_name = "CI/CD Service Account"
  description  = "Service account for running CI/CD from Bitbucket."
}

resource "google_project_iam_member" "cicd_service_account_iam" {
  for_each = toset(var.svc_cicd_roles)
  role     = each.key
  project  = var.project
  member   = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

# It's possible to restrict the `member` property even more:
# https://cloud.google.com/iam/docs/workload-identity-federation#impersonation
resource "google_service_account_iam_member" "workload_identity_user_iam" {
  service_account_id = google_service_account.cicd_service_account.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.cicd_identity_pool.name}/*"
}
