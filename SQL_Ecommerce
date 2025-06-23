- This file contains SQL queries to interact with your raw e-commerce clickstream data
-- in Amazon Athena, using the schema defined by AWS Glue.

-- IMPORTANT: Replace "ecommerce_raw_db" with your actual Glue database name if different.
-- IMPORTANT: Replace "data" with your actual table name if Glue crawler inferred a different name (ee.g., 'ecommerce_data').
-- Note: Athena query results will be stored in your configured S3 query results bucket.

-- Query 1: Preview the first 10 rows of the raw data table
-- This helps confirm that Athena can access the table and read the data correctly.
SELECT *
FROM "ecommerce_raw_db"."data"  -- Adjust "data" if your table name is different (e.g., "ecommerce_data")
LIMIT 10;

-- Query 2: Count of all events in the raw data
-- This gives you a quick overview of the total number of records.
SELECT count(*)
FROM "ecommerce_raw_db"."data"; -- Adjust "data" if your table name is different

-- Query 3: Events by type for a specific day (Leveraging Partitions)
-- This demonstrates filtering data efficiently using the 'year', 'month', 'day' partition columns.
-- Athena will only scan the files within the specified partitions, saving cost and time.
SELECT
    event_type,
    count(*) AS event_count
FROM "ecommerce_raw_db"."data"
WHERE year = '2025' AND month = '06' AND day = '23' -- Specify the partition values
GROUP BY event_type
ORDER BY event_count DESC;

-- Query 4: Total purchases and average price by date
-- This showcases basic aggregations and filtering on event types.
-- Note: 'price' might be a string in raw data, so casting to DOUBLE might be necessary if it fails.
SELECT
    CAST(timestamp AS DATE) AS event_date,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS total_purchases,
    AVG(CASE WHEN event_type = 'purchase' THEN CAST(price AS DOUBLE) ELSE NULL END) AS average_purchase_price
FROM "ecommerce_raw_db"."data"
WHERE event_type = 'purchase' AND price IS NOT NULL
GROUP BY CAST(timestamp AS DATE)
ORDER BY event_date;

-- Query 5: Top 5 most viewed products (using Product ID)
-- A common analytical query to identify popular products from 'product_view' events.
SELECT
    product_id,
    count(*) AS view_count
FROM "ecommerce_raw_db"."data"
WHERE event_type = 'product_view' AND product_id IS NOT NULL
GROUP BY product_id
ORDER BY view_count DESC
LIMIT 5;

-- You can write more complex SQL queries here as you learn more about Athena and SQL.
-- Try joining different fields, using window functions, or extracting more insights!
