provider "databricks" {
  # auth_type = "github-oidc"
  host          = var.databricks_workspace_url
  client_id     = var.databricks_client_id
  client_secret = var.databricks_client_secret
}