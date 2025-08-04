terraform {
  backend "s3" {
    bucket = "ecom-data-sync-infra"
    key    = "dev/terraform.tfstate"
    region = "eu-north-1"
  }
}