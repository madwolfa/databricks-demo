# databricks-demo
Repository for Databricks Demo Terraform workspace

## Terraform
This Terraform [code](./main.tf) creates a managed table in an existing catalog and schema, replicates the schema from a source table, and sets up a job to copy data using a merge query.

### Prerequisites
  1. Catalog `sandbox` has been created manually in the Databricks UI with the default storage.
  2. Service principal `TERRAFORM_ADMIN` has been created with all privileges granted to it.
  3. Credentials have been generated and stored as secure variables inside TFC workspace:
        - `databricks_workspace_url`
        - `databricks_client_id`
        - `databricks_client_secret`
  4. Environment specific configuration added to [terraform.auto.tfvars](./terraform.auto.tfvars) file.

### Execution
This IaC is executed using the `Terraform Apply` GitHub Action [workflow](./.github/workflows/terraform-apply.yml). Terraform Cloud is used as a backend.
Speculative plans are supported using the `Terraform Plan` GitHub Action [workflow](./.github/workflows/terraform-plan.yml) as part of PR review process.

## Python
This [script](./scripts/modify_job.py) modifies the schedule of a Databricks job to run on weekdays only or every day based on the environment variable `WEEKDAYS_ONLY`. It uses the Databricks SDK for Python to interact with the Databricks workspace.

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