from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

job_list = w.jobs.list()

for j in job_list:
    print(f"Job ID: {j.job_id}, State: {j.state}")
