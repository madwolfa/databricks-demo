# databricks-demo
Repository for Databricks Demo Terraform workspace

## Terraform
This Terraform [code](./main.tf) creates a new schema and managed table in an existing catalog, and sets up a scheduled job to copy data from the source table using the `MERGE INTO` [SQL query](https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into).

### Query
The source table schema is replicated with an added `row_hash` column. Since there is no unique key in the original table, a hash value derived from all columns will be used for reliable row identification. Using on-the-fly hash comparison, the query will insert new, unique rows and delete rows that are no longer present in the source table.

```sql
-- Use merge with schema evolution to copy data from the source table to the managed table
-- https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into#with-schema-evolution
MERGE WITH SCHEMA EVOLUTION INTO
  sandbox.nyctaxi.trips AS target
USING (
  SELECT
    -- Select all columns from the source table
    *,
    -- Create a hash of all columns to identify unique rows
    -- Put it into a new 'row_hash' column
    sha2(concat_ws('||', *), 256) AS row_hash
  FROM
    samples.nyctaxi.trips
) AS source
-- Compare the 'row_hash' values to identify matching rows
ON
  target.row_hash = source.row_hash
-- If not matched, insert the new row
WHEN NOT MATCHED THEN INSERT *
-- If not present in the source, delete the row
WHEN NOT MATCHED BY SOURCE THEN DELETE
```

### Prerequisites
  1. Catalog `sandbox` created manually in the Databricks workspace UI with the default storage.
  2. Service principal `TERRAFORM_ADMIN` created with `ALL PRIVILEGES` granted on the catalog.
  3. Credentials generated and stored as secure variables inside Terraform Cloud workspace:
        - `databricks_workspace_url`
        - `databricks_client_id`
        - `databricks_client_secret`
  4. Environment specific configuration added to [terraform.auto.tfvars](./terraform.auto.tfvars) file.

### Execution
This IaC is executed using the `Terraform Apply` GitHub Action [workflow](./.github/workflows/terraform-apply.yml). Terraform Cloud is used as a backend. 

Speculative plans are supported using the `Terraform Plan` GitHub Action [workflow](./.github/workflows/terraform-plan.yml) as part of PR review process.

## Python
This [script](./scripts/modify_job.py) modifies the schedule of a Databricks job to run on weekdays only or every day based on the environment variable `WEEKDAYS_ONLY`. It uses the [Databricks SDK for Python](https://docs.databricks.com/aws/en/dev-tools/sdk-python) to interact with the Databricks workspace.

### Prerequisites
The script expects the following variables to be set in the environment (we pass all of these through GitHub Actions):
   - `DATABRICKS_HOST`: The URL of the Databricks workspace.
   - `DATABRICKS_CLIENT_ID`: The client ID of the service principal.
   - `DATABRICKS_CLIENT_SECRET`: The client secret of the service principal.
   - `JOB_NAME`: The name of the job to modify.
   - `WEEKDAYS_ONLY`: A boolean value indicating whether to run the job on weekdays only (True) or every day (False).

### Execution
The script is executed using the `Python CI` GitHub Action [workflow](./.github/workflows/python.yml) which requires the following inputs:
   - `job_name` (string): Name of the job to modify
   - `weekdays_only` (boolean): Should the job run only on weekdays?