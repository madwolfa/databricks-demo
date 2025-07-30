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
    """Returns a cron expression with the specified parts updated.

    Args:
      cron (str): The cron expression to update.
      **kwargs: Keyword arguments specifying the parts to update
                (e.g., seconds, minutes, hours, dom, month, dow).
    """
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


def update_job(job_name="", weekdays_only=False):
    """Returns True if the job schedule was updated successfully

    This function updates the schedule of a Databricks job to run on weekdays only or every day based on the value of the `weekdays_only` parameter.
    If the job is not found or more than one is found - it raises an exception, otherwise it updates the schedule of the job and returns True.

    Args:
      job_name (str): The name of the job to update.
      weekdays_only (bool): Whether to run the job on weekdays only (True) or every day (False).
    """
    if not job_name:
        raise Exception("Please provide a job name!")

    job_list = w.jobs.list(name=job_name)

    job_ids = []
    for j in job_list:
        job_ids.append(j.job_id)

    if len(job_ids) > 1:
        print(f"Found more than one job with name '{job_name}': {job_ids}")
        raise Exception(f"Found more than one job with name '{job_name}'.")
    elif len(job_ids) == 1:
        job_id = job_ids[0]
        print(f"Found job ID with name '{job_name}': {job_id}")
    else:
        job_id = 0

    if job_id:
        current_schedule = w.jobs.get(job_id=job_id).settings.schedule
        print(f"Current job schedule: {current_schedule.as_dict()}")
        cron_expression = current_schedule.quartz_cron_expression
        timezone_id = current_schedule.timezone_id
        if weekdays_only:
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
        return True
    else:
        print(f"Job with name '{job_name}' not found!")
        raise Exception(f"Job with name '{job_name}' not found!")


if __name__ == "__main__":
    update_job(job_name=JOB_NAME, weekdays_only=WEEKDAYS_ONLY)