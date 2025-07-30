from os import getenv
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

run_list = w.jobs.list_runs()

for j in run_list:
    print(f"Run ID: {j.run_id}, State: {j.state}, Job ID: {j.job_id}")
