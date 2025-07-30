catalog_name = "sandbox"

job_name        = "SQL Copy Job"
job_description = "This job copies data from the source table to the managed table using a SQL query."
job_tags        = {}

quartz_cron_expression = "0 0 12 * * ?" # Default to daily at noon
timezone_id            = "UTC"          # Default to UTC