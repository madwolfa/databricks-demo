import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

JOB_NAME = os.getenv("JOB_NAME", "SQL Copy Job")
WEEKDAYS_ONLY = os.getenv("WEEKDAYS_ONLY", "False").lower() == "true"

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