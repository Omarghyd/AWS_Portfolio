AWS Serverless Data Lake for E-commerce Clickstream Data
Project Overview
This project demonstrates the foundational steps of building a serverless data lake on Amazon Web Services (AWS) for handling e-commerce clickstream data. It covers data ingestion into S3, schema discovery and cataloging using AWS Glue, and interactive querying with Amazon Athena. This is a crucial starting point for any data engineering pipeline that aims to analyze large volumes of semi-structured data.

The goal is to set up an environment where raw, event-driven data can land, its structure can be automatically understood, and it can be immediately queried using standard SQL, without managing any servers.

AWS Services Used
Amazon S3 (Simple Storage Service): Used as the primary storage layer for the data lake.

yourname-ecomm-raw-data-lake: Stores the raw, unprocessed clickstream data.

yourname-athena-query-results: Stores the results of Athena queries.

(Future) yourname-ecomm-processed-data-lake: Will store cleaned and transformed data.

AWS IAM (Identity and Access Management): Manages permissions for AWS services to interact with each other. A dedicated IAM Role grants AWS Glue the necessary access to S3 and the Data Catalog.

AWS Glue: A serverless data integration service.

Glue Data Catalog: A central metadata repository that stores schema information for data in S3.

Glue Crawler: Automatically scans data in S3, infers schemas, and populates the Data Catalog.

Amazon Athena: An interactive query service that allows you to analyze data directly in S3 using standard SQL, leveraging the schema from the Glue Data Catalog.

AWS CloudWatch: For monitoring service activities and logs.

Architecture (High-Level)
+----------------+       +-------------------+       +---------------------+
| E-commerce     |       | Amazon S3         |       | AWS Glue            |
| Application    +-----> | (Raw Data Bucket) |       | (Data Catalog,      |
| (Simulated)    |       |   - JSON Lines    |       |  Crawler)           |
|                |       |   - Partitioned   |       |                     |
+----------------+       |     data/raw/     |       +----------^----------+
                         |      year=/       |                  |
                         |      month=/      |                  |
                         |      day=/        |                  |
                         +----------+--------+                  |
                                    |                           |
                                    | (Schema Discovery)        |
                                    v                           |
                         +---------------------------------+    |
                         | AWS Glue Data Catalog           |----+
                         | (Metadata for raw data table)   |
                         +---------------------------------+
                                    ^
                                    | (SQL Queries)
                                    |
                         +---------------------+
                         | Amazon Athena       |
                         | (Interactive SQL)   |
                         |   - Query Results   |
                         |     (to S3)         |
                         +---------------------+

Project Setup Guide
This section outlines the steps to replicate the environment demonstrated in this project.

AWS Account: Ensure you have an active AWS account. Set up billing alerts in CloudWatch to monitor your spending (highly recommended for new accounts).

S3 Bucket Creation:

Create three S3 buckets in your preferred AWS Region (e.g., us-east-1):

yourname-ecomm-raw-data-lake (for raw input data)

yourname-ecomm-processed-data-lake (for future processed data)

yourname-athena-query-results (for Athena's query output)

Ensure "Block all public access" is enabled for all buckets (default and recommended).

IAM Role for AWS Glue:

Go to IAM Console > Roles > Create role.

Trusted entity: "AWS service", then select "Glue" as the use case.

Permissions: Attach managed policies AWSGlueServiceRole and AmazonS3FullAccess. (In production, use more granular S3 permissions).

Role name: e.g., GlueDataEngineerRole.

Data Preparation and Upload:

Locally, create the following directory structure:

data/
└── raw/
    ├── year=2025/
    │   └── month=06/
    │       ├── day=23/
    │       │   ├── events_1.json
    │       │   └── events_2.json
    │       └── day=24/
    │           └── events_today.json

Populate the .json files with the sample data provided in the data/raw/ directory of this repository. Remember, each line in the JSON files is a separate JSON object (JSON Lines format).

Upload the entire data/ folder (including its subdirectories and files) to your yourname-ecomm-raw-data-lake S3 bucket. The path in S3 should look like s3://yourname-ecomm-raw-data-lake/data/raw/year=2025/month=06/day=23/events_1.json, etc.

AWS Glue Database & Crawler Configuration:

Go to AWS Glue Console.

Create Database: Navigate to "Data Catalog" > "Databases" > "Add database". Name it ecommerce_raw_db.

Create Crawler: Navigate to "Data Catalog" > "Crawlers" > "Create crawler".

Name: ecommerce_raw_crawler

Data source: "S3", point to s3://yourname-ecomm-raw-data-lake/data/raw/

IAM role: Select the GlueDataEngineerRole you created.

Output: Select ecommerce_raw_db as the database.

Schedule: "Run on demand".

Run the Crawler: Select ecommerce_raw_crawler and click "Run crawler". Wait for it to complete.

Verify a new table (likely named raw) is created in ecommerce_raw_db under Glue's "Tables" section, with year, month, day identified as partition columns.

Amazon Athena Query Setup & Execution:

Go to Amazon Athena Console.

Set Query Result Location: In "Settings", configure the query result location to your s3://yourname-athena-query-results/ bucket.

Select Database: On the left, ensure AwsDataCatalog is selected, and then choose ecommerce_raw_db.

Query: Use the queries provided in sql/athena_raw_data_queries.sql to explore your raw data. Remember to use double quotes around database and table names, e.g., "ecommerce_raw_db"."data".

Project Structure (GitHub Repository)
.
├── README.md
├── data/
│   └── raw/
│       ├── year=2025/
│       │   └── month=06/
│       │       ├── day=23/
│       │       │   ├── events_1.json
│       │       │   └── events_2.json
│       │       └── day=24/
│       │           └── events_today.json
├── sql/
│   └── athena_raw_data_queries.sql
└── glue_scripts/
    └── etl_raw_to_processed.py

Key Learnings & Demonstrated Skills
By completing this project, you will have demonstrated:

Cloud Fundamentals: Basic navigation and understanding of the AWS ecosystem.

Data Lake Foundations: Setting up scalable and cost-effective object storage (S3) for raw data.

Metadata Management: Using AWS Glue to automatically discover and catalog data schemas, including partitioned data.

Serverless Querying: Performing ad-hoc SQL queries on data directly in S3 using Amazon Athena.

Data Organization: Implementing date-based partitioning for performance optimization.

Troubleshooting: Identifying and resolving common issues (like TABLE_NOT_FOUND).

Best Practices Awareness: Understanding the trade-offs of using AmazonS3FullAccess vs. granular policies, and the importance of partitioning.

Future Enhancements (Next Steps to Intermediate)
This project serves as a strong foundation. To further enhance it and showcase more advanced data engineering skills, consider:

ETL with AWS Glue Jobs:

Write a PySpark script (using glue_scripts/etl_raw_to_processed.py) to read the raw JSON data, perform transformations (e.g., flatten complex fields, clean data types, calculate new metrics), and write the output as optimized Parquet files to the yourname-ecomm-processed-data-lake bucket.

Run a new Glue Crawler on the processed data to catalog its schema.

Data Visualization: Connect Amazon QuickSight (AWS's BI tool) to your processed data in Athena/Glue to create interactive dashboards.

Workflow Orchestration: Use AWS Step Functions to automate the entire pipeline (triggering the raw data crawler, then the ETL job, then a processed data crawler).

Streaming Data Ingestion: Explore integrating AWS Kinesis Data Firehose to simulate real-time data ingestion into your raw S3 bucket.

Infrastructure as Code (IaC): Use AWS CloudFormation or Terraform to define and deploy all your AWS resources programmatically, ensuring reproducibility and version control.

Data Quality Checks: Add logic within your Glue ETL job to validate data quality and handle bad records.

Cost Optimization: Deep dive into Glue job configurations (DPUs, worker types) to optimize performance and cost.
