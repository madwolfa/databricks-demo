### Below credentials for OAuth authorization are consumed from TFC workspace environment variables
### They have been generated for 'TERRAFORM_ADMIN' service principal inside Databricks workspace
# databricks_workspace_url = ""
# databricks_client_id     = ""
# databricks_client_secret = ""
catalog_name      = "sandbox"
schema_name       = "nyctaxi"
warehouse_name    = "Serverless Starter Warehouse"
source_table_name = "samples.nyctaxi.trips"
target_table_name = "trips"

job_name        = "SQL Copy Job"
job_description = "This job copies data from the source table to the managed table using a SQL query."
job_tags        = {}

query_name        = "Copy Data Query"
query_description = "This query copies data from the source table to the managed table."
query_tags        = []

quartz_cron_expression = "0 0 9 * * ?"
timezone_id            = "UTC-05:00" # CDT (Central Daylight Time)