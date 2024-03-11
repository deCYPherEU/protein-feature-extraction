variable "project" {
  description = "GCP project name"
  type        = string
}

variable "attribute_condition" {
  description = "See https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iam_workload_identity_pool_provider#attribute_condition"
  type        = string
}

variable "attribute_mapping" {
  description = "See https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iam_workload_identity_pool_provider#attribute_mapping"
  type        = map(string)
  default = {
    "google.subject" = "assertion.sub",
  }
}

variable "audiences" {
  description = "See https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iam_workload_identity_pool_provider#allowed_audiences"
  type        = list(string)
  default     = []
}

variable "issuer_uri" {
  description = "The OIDC issuer URL"
  type        = string
}

variable "cicd_service_account_id" {
  description = "Name of the service account that will be available through the identity pool."
  type        = string
}

variable "svc_cicd_roles" {
  description = "IAM roles to bind on CI/CD service account"
  type        = list(string)
}
