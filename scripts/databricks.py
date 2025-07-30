from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

run_list = w.jobs.list_runs()

print(run_list)