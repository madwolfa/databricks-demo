/* 
   Summary:    
     This Terraform code creates a managed table in an existing catalog and schema, replicates the 
     schema from a source table, and sets up a job to copy data using a merge query.
    
   Prerequisites:
      1. Catalog 'sandbox' created manually in the Databricks workspace UI with the default storage.
      2. Service principal 'TERRAFORM_ADMIN' created with 'ALL PRIVILEGES' granted on the catalog.
      3. Credentials generated and stored as secure variables inside TFC workspace:
         - databricks_workspace_url
         - databricks_client_id
         - databricks_client_secret
         - databricks_region
    4. Environment specific configuration added to 'terraform.auto.tfvars' file.
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

# Use merge query to copy data from the source table to the managed table
# Since there is no unique key in the source table, we will use a hash of all columns to identify rows
# The query will insert new unique rows and delete rows that are no longer present in the source table
resource "databricks_query" "this" {
  warehouse_id = data.databricks_sql_warehouse.this.id
  query_text   = <<EOT
-- Use merge with schema evolution to copy data from the source table to the managed table
-- https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into#with-schema-evolution
MERGE WITH SCHEMA EVOLUTION INTO
  ${databricks_sql_table.this.id} AS target
USING (
  SELECT
    -- Select all columns from the source table
    *,
    -- Create a hash of all columns to identify unique rows
    -- Put it into a new 'row_hash' column
    sha2(concat_ws('||', *), 256) AS row_hash
  FROM
    ${data.databricks_table.source.name}
) AS source
-- Compare the 'row_hash' values to identify matching rows
ON
  target.row_hash = source.row_hash
-- If not matched, insert the new row
WHEN NOT MATCHED THEN INSERT *
-- If not present in the source, delete the row
WHEN NOT MATCHED BY SOURCE THEN DELETE
EOT
  display_name = var.query_name
  description  = var.query_description

  tags = var.query_tags
}

# Create job definition to run the copy query
resource "databricks_job" "this" {
  name        = var.job_name
  description = var.job_description

  task {
    # Remove special characters for task key
    task_key = replace("Run ${databricks_query.this.display_name}", "/[^a-zA-Z0-9]/", "_")
    sql_task {
      warehouse_id = data.databricks_sql_warehouse.this.id
      query {
        query_id = databricks_query.this.id
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