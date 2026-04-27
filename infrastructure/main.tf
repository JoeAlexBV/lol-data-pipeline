# ============================================
# Terraform Configuration for LoL Data Pipeline
# ============================================
# This provisions the AWS infrastructure needed
# to run the pipeline. 
#
# Usage:
#   cd infrastructure
#   terraform init
#   terraform plan
#   terraform apply
# ============================================

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------- VARIABLES ----------

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-2"
}

variable "bucket_name" {
  description = "Name of the S3 Data Lake bucket"
  type        = string
  default     = "joebv-lol-data-lake"
}

variable "athena_database" {
  description = "Name of the Athena database"
  type        = string
  default     = "default"
}

# ---------- S3 DATA LAKE ----------

resource "aws_s3_bucket" "data_lake" {
  bucket = var.bucket_name

  tags = {
    Project     = "lol-data-pipeline"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake_public_access" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_encryption" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 folder structure (prefix objects)
resource "aws_s3_object" "raw_folder" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "raw/"
}

resource "aws_s3_object" "processed_folder" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "processed/"
}

resource "aws_s3_object" "athena_results_folder" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "athena-results/"
}

# ---------- IAM USER FOR PIPELINE ----------

resource "aws_iam_user" "pipeline_user" {
  name = "lol-pipeline-user"

  tags = {
    Project   = "lol-data-pipeline"
    ManagedBy = "terraform"
  }
}

resource "aws_iam_user_policy_attachment" "s3_access" {
  user       = aws_iam_user.pipeline_user.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_user_policy_attachment" "athena_access" {
  user       = aws_iam_user.pipeline_user.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

# ---------- ATHENA ----------

resource "aws_athena_named_query" "create_table" {
  name        = "create_fact_match_participant"
  database    = var.athena_database
  description = "Creates the fact_match_participant table over the processed S3 data"
  query       = file("../sql/create_athena_table.sql")
  workgroup   = "primary"
}

# ---------- OUTPUTS ----------

output "s3_bucket_name" {
  value = aws_s3_bucket.data_lake.id
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.data_lake.arn
}

output "pipeline_user_name" {
  value = aws_iam_user.pipeline_user.name
}