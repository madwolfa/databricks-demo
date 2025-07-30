import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

JOB_NAME = os.getenv("JOB_NAME", "SQL Copy Job")
CRON_EXPRESSION = os.getenv("CRON_EXPRESSION", "0 0 12 * * ?")
TIMEZONE_ID = os.getenv("TIMEZONE_ID", "UTC")

w = WorkspaceClient()

job_list = w.jobs.list(name=JOB_NAME)
for j in job_list:
    job_id = j.job_id

current_settings = w.jobs.get(job_id=job_id).settings
print("Current job schedule:\n", str(current_settings.schedule.as_dict()))

new_settings = jobs.JobSettings(
    schedule=jobs.CronSchedule(
        quartz_cron_expression=CRON_EXPRESSION, timezone_id=TIMEZONE_ID
    )
)
print("New job schedule:\n", str(new_settings.schedule.as_dict()))

try:
    res = w.jobs.update(job_id=job_id, new_settings=new_settings)
except Exception as e:
    print("Oops!", e)