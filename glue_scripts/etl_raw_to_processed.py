
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# --- 1. Extract (Read from Raw Data Lake) ---
# Read the raw data from the Glue Data Catalog table created by the crawler.
# This assumes your Glue database is 'ecommerce_raw_db' and the table is 'data'.
# Adjust these names if your crawler created something different.
raw_data_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="ecommerce_raw_db",
    table_name="data", # Make sure this matches the actual table name Glue created (e.g., 'ecommerce_data')
    transformation_ctx="raw_data_source"
)

# --- 2. Transform (Example Transformations) ---
# Convert DynamicFrame to Spark DataFrame for easier manipulation
raw_data_df = raw_data_dyf.toDF()

# Example Transformation 1: Flattening the schema (if there were nested JSON objects)
# For our current sample data, the schema is already flat, but this is how you'd handle it.
# If your data has deeply nested structures, you might use Relationalize or explicit flattening.
# Example: If 'user' was a struct: raw_data_df.selectExpr("user.*", "*").drop("user")

# Example Transformation 2: Type casting for numerical fields
# Ensure 'price' and 'quantity' are numerical types for calculations.
from pyspark.sql.functions import col
processed_data_df = raw_data_df.withColumn("price", col("price").cast("double")) \
                               .withColumn("quantity", col("quantity").cast("integer")) \
                               .withColumn("timestamp", col("timestamp").cast("timestamp"))

# Example Transformation 3: Add a derived column (e.g., 'event_date_only')
from pyspark.sql.functions import to_date
processed_data_df = processed_data_df.withColumn("event_date_only", to_date(col("timestamp")))

# Example Transformation 4: Select and reorder columns, drop unnecessary ones
# This is a good practice to curate your processed data.
processed_data_df = processed_data_df.select(
    "event_id",
    "timestamp",
    "event_date_only", # New derived column
    "user_id",
    "session_id",
    "event_type",
    "page_url",
    "product_id",
    "category",
    "price",
    "quantity",
    "payment_method",
    "browser",
    "os"
)

# Convert back to DynamicFrame for Glue's sink operations (optional, but good practice for Glue)
processed_data_dyf = DynamicFrame.fromDF(processed_data_df, glueContext, "processed_data_dynamic_frame")

# --- 3. Load (Write to Processed Data Lake) ---
# Write the processed data to the processed S3 bucket in Parquet format.
# We will partition the processed data by year, month, and day for optimal querying.
# Make sure your 'yourname-ecomm-processed-data-lake' bucket exists.
output_path = "s3://yourname-ecomm-processed-data-lake/processed_events/"

processed_data_sink = glueContext.getSink(
    connection_type="s3",
    path=output_path,
    enableUpdateCatalog=True,
    updateBehavior="UPDATE_IN_DATABASE", # Recommended for partitioning
    partitionKeys=["year", "month", "day"], # These are derived from the 'timestamp' in the raw data
                                             # Ensure the raw_data_dyf correctly passes these from S3 path.
    compression="snappy", # Snappy compression is a good default for Parquet
    format="parquet",
    transformation_ctx="processed_data_sink"
)

# Write the DynamicFrame to S3
processed_data_sink.setCatalogInfo(
    catalogDatabase="ecommerce_processed_db", # This database will be created/updated by Glue.
    tableName="events"                         # This table will store the processed data.
)
processed_data_sink.setRelaunch(True) # Allows the job to restart on failure
processed_data_sink.writeFrame(processed_data_dyf)

job.commit()
