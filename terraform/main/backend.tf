
/******************************************
	Remote backend configuration
 *****************************************/

# setup of the backend gcs bucket that will keep the remote state

terraform {
  backend "gcs" {
    bucket = "elated-chassis-400207_terraform"
    prefix = "terraform/state"
  }
}
