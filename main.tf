resource "databricks_catalog" "sandbox" {
  name           = "sandbox"
  isolation_mode = "ISOLATED"
  comment        = "This catalog is managed by Terraform"

  properties = {
    purpose = "testing"
  }
}