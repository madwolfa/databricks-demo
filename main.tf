# Catalog had to be created manually in the Databricks UI before running this Terraform code.
# Full privileges have been granted to the TERRAFORM_ADMIN service principal.
data "databricks_catalog" "this" {
  name = "sandbox"
}

output "catalog_info" {
  value = data.databricks_catalog.this.catalog_info[0]
}