variable "databricks_workspace_url" {
  description = "The URL of the Databricks workspace."
  type        = string
}

variable "databricks_client_id" {
  description = "The client ID for the Databricks workspace."
  type        = string
}

variable "databricks_client_secret" {
  description = "The client secret for the Databricks workspace."
  type        = string
  sensitive   = true
}

variable "catalog_name" {
  description = "The name of the Databricks catalog to use."
  type        = string
  default     = "sandbox"
}

variable "schema_name" {
  description = "The name of the schema (database) to create in the catalog."
  type        = string
  default     = "nyctaxi"
}

variable "warehouse_name" {
  description = "The name of the Databricks SQL warehouse to use."
  type        = string
  default     = "Serverless Starter Warehouse"
}

variable "source_table_name" {
  description = "The name of the source table to copy data from."
  type        = string
  default     = "samples.nyctaxi.trips"
}

variable "target_table_name" {
  description = "The name of the target table to create in the schema."
  type        = string
  default     = "trips"
}

variable "job_name" {
  description = "The name of the Databricks job to create or update."
  type        = string
  default     = "SQL Copy Job"
}

variable "job_description" {
  description = "A description for the Databricks job."
  type        = string
  default     = "This job is managed by Terraform"
}

variable "job_tags" {
  description = "Tags to apply to the Databricks job."
  type        = map(string)
  default     = {}
}

variable "quartz_cron_expression" {
  description = "The cron expression for the job schedule."
  type        = string
  default     = "0 0 12 * * ?"
}

variable "timezone_id" {
  description = "The timezone ID for the job schedule."
  type        = string
  default     = "UTC"
}

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}