from os import getenv
from databricks.sdk import WorkspaceClient

databricks_host = getenv("DATABRICKS_HOST")
databricks_client_id = getenv("DATABRICKS_CLIENT_ID")
databricks_client_secret = getenv("DATABRICKS_CLIENT_SECRET")

print(databricks_host)
print(databricks_client_id)

w = WorkspaceClient(
  host          = databricks_host,
  client_id     = databricks_client_id,
  client_secret = databricks_client_secret
)

run_list = w.jobs.list_runs()

print(run_list)