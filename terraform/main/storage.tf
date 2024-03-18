/******************************************
  State storage configuration
 *****************************************/

resource "google_storage_bucket" "terraform_state" {
  name                        = "${var.project}_dbtl_pipeline_outputs"
  location                    = var.region
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}
