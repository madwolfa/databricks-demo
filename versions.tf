terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
      version = "~> 1.85.0"
    }
  }
  required_version = ">= 1.12.0"
}
