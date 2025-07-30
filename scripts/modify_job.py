from databricks.sdk import WorkspaceClient
from databricks.sdk.service import catalog

w = WorkspaceClient()

all = w.catalogs.list(catalog.ListCatalogsRequest())

for c in all:
    print(c.name)

job_list = w.jobs.list()

print(job_list)

for j in job_list:
    print(j)
