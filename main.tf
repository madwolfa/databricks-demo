resource "databricks_catalog" "sandbox" {
  name         = "sandbox"
  comment      = "This catalog is managed by Terraform"
  properties = {
    purpose = "testing"
  }
}