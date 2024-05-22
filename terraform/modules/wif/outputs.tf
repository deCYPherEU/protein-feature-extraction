output "workload_identity_provider" {
  value = google_iam_workload_identity_pool_provider.cicd_identity_provider.name
}
