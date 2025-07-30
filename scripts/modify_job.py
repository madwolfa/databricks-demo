from databricks.sdk import WorkspaceClient
from databricks.sdk.service import catalog

w = WorkspaceClient()

all = w.catalogs.list()

for c in all:
    print(c.name)

job_list = w.jobs.list(name="SQL Copy Job")

job_id = job_list[0].job_id
print(job_id)

print(job_list)

for j in job_list:
    print(j)
