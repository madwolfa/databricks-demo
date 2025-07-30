from os import getenv
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(
  host          = getenv("DATABRICKS_HOST"),
  client_id     = getenv("DATABRICKS_CLIENT_ID"),
  client_secret = getenv("DATABRICKS_CLIENT_SECRET")
)

run_list = w.jobs.list_runs()

print(run_list)