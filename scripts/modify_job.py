"""
  This script modifies the schedule of a Databricks job to run on weekdays only or every day based on the environment variable WEEKDAYS_ONLY.
  It uses the Databricks SDK for Python to interact with the Databricks workspace.

  It expects the following variables to be set in the environment:
    - DATABRICKS_HOST: The URL of the Databricks workspace.
    - DATABRICKS_CLIENT_ID: The client ID of the service principal.
    - DATABRICKS_CLIENT_SECRET: The client secret of the service principal.
    - JOB_NAME: The name of the job to modify.
    - WEEKDAYS_ONLY: A boolean value indicating whether to run the job on weekdays only (True) or every day (False).

  References:
    1. https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html
    2. https://docs.databricks.com/aws/en/dev-tools/sdk-python
    3. https://databricks-sdk-py.readthedocs.io/en/latest/getting-started.html
    4. https://databricks-sdk-py.readthedocs.io/en/latest/workspace/jobs/jobs.html
    5. https://databricks-sdk-py.readthedocs.io/en/latest/dbdataclasses/jobs.html#databricks.sdk.service.jobs.JobSettings
    6. https://databricks-sdk-py.readthedocs.io/en/latest/dbdataclasses/jobs.html#databricks.sdk.service.jobs.CronSchedule
"""

import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

JOB_NAME = os.getenv("JOB_NAME", "SQL Copy Job")
WEEKDAYS_ONLY = os.getenv("WEEKDAYS_ONLY", "False").lower() == "true"

# Initialize the WorkspaceClient with environment variables
w = WorkspaceClient()


# Helper function to update cron expression
def update_cron(cron, **kwargs):
    parts = cron.split(" ")
    if len(parts) != 6:
        raise Exception(f"Invalid cron expression: {cron}")
    seconds, minutes, hours, dom, month, dow = (
        kwargs.get("seconds", parts[0]),
        kwargs.get("minutes", parts[1]),
        kwargs.get("hours", parts[2]),
        kwargs.get("dom", parts[3]),
        kwargs.get("month", parts[4]),
        kwargs.get("dow", parts[5]),
    )
    return " ".join(
        # Cast all parts to string for safety
        [str(seconds), str(minutes), str(hours), str(dom), str(month), str(dow)]
    )


job_list = w.jobs.list(name=JOB_NAME)

job_ids = []
for j in job_list:
    job_ids.append(j.job_id)

if len(job_ids) > 1:
    print(f"Found more than one job with name '{JOB_NAME}': {job_ids}")
    raise Exception(f"Found more than one job with name '{JOB_NAME}'.")
elif len(job_ids) == 1:
    job_id = job_ids[0]
    print(f"Found job ID with name '{JOB_NAME}': {job_id}")
else:
    job_id = 0

if job_id:
    current_settings = w.jobs.get(job_id=job_id).settings
    print(f"Current job schedule: {current_settings.schedule.as_dict()}")
    cron_expression = current_settings.schedule.quartz_cron_expression
    timezone_id = current_settings.schedule.timezone_id
    if WEEKDAYS_ONLY:
        cron_expression = update_cron(cron_expression, dom="?", dow="MON-FRI")
    else:
        cron_expression = update_cron(cron_expression, dom="*", dow="?")
    new_settings = jobs.JobSettings(
        schedule=jobs.CronSchedule(
            quartz_cron_expression=cron_expression,
            timezone_id=timezone_id,
        )
    )
    print(f"New job schedule: {new_settings.schedule.as_dict()}")
    w.jobs.update(job_id=job_id, new_settings=new_settings)
    print("Job schedule updated!")
else:
    print(f"Job with name '{JOB_NAME}' not found!")
    raise Exception(f"Job with name '{JOB_NAME}' not found!")