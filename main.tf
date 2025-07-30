/* 
   Prerequisites:
     1. Catalog has been created manually in the Databricks UI with the default storage.
     2. Service principal 'TERRAFORM_ADMIN' has been created with all privileges granted to it.
*/

# This Terraform code assumes that the catalog already exists. Let's look it up:
data "databricks_catalog" "this" {
  name = var.catalog_name
}

# Output the catalog information
output "catalog_info" {
  value = data.databricks_catalog.this.catalog_info[0]
}

# Create a schema (database) in the existing catalog
resource "databricks_schema" "this" {
  catalog_name = data.databricks_catalog.this.id
  name         = var.schema_name
  comment      = "This database is managed by Terraform"
  properties = {
    catalog = data.databricks_catalog.this.name
    owner   = "TERRAFORM_ADMIN"
  }
}

# Let's lookup our serverless SQL warehouse
data "databricks_sql_warehouse" "this" {
  name = var.warehouse_name
}

# Lookup the source table to extract its schema
data "databricks_table" "source" {
  name = var.source_table_name
}

# Create a managed table in the schema
resource "databricks_sql_table" "this" {
  name         = var.target_table_name
  catalog_name = data.databricks_catalog.this.name
  schema_name  = databricks_schema.this.name
  table_type   = "MANAGED"
  warehouse_id = data.databricks_sql_warehouse.this.id

  # Replicate the source table schema
  dynamic "column" {
    for_each = data.databricks_table.source.table_info[0].columns
    content {
      name = column.value.name
      type = column.value.type_text
    }
  }
  # Add a computed column for row hash
  column {
    name = "row_hash"
    type = "string"
  }

  comment = "This table is managed by Terraform"
}

resource "databricks_query" "copy_query" {
  warehouse_id = data.databricks_sql_warehouse.this.id
  query_text   = <<EOT
MERGE WITH SCHEMA EVOLUTION INTO
  ${databricks_sql_table.this.id} AS target
USING (
  SELECT
    *,
    sha2(concat_ws('||', *), 256) AS row_hash
  FROM
    ${data.databricks_table.source.name}
) AS source
ON
  target.row_hash = source.row_hash
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE
EOT
  display_name = "Copy Query"
}

resource "databricks_job" "sql_copy_job" {
  name        = var.job_name
  description = var.job_description

  task {
    task_key = "run_copy_query"
    sql_task {
      warehouse_id = data.databricks_sql_warehouse.this.id
      query {
        query_id = databricks_query.copy_query.id
      }
    }
  }
  schedule {
    quartz_cron_expression = var.quartz_cron_expression
    timezone_id            = var.timezone_id
  }

  tags = var.job_tags

  lifecycle {
    ignore_changes = [
      # Ignore changes to the schedule outside of Terraform
      schedule
    ]
  }
}