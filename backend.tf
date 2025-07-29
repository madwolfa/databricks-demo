terraform {
  cloud {
    organization = "Foobar_Org"
    hostname     = "app.terraform.io"

    workspaces {
      name = "databricks-demo"
    }
  }
}