from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Create View for Feast Trino Offline Store") \
    .config("spark.driver.extraClassPath", "/opt/bitnami/spark/jars/*") \
    .config("spark.executor.extraClassPath", "/opt/bitnami/spark/jars/*") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "https://minio.minio.svc.cluster.local:443") \
    .config("spark.hadoop.fs.s3a.access.key", "minio") \
    .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("hive.metastore.uris", "thrift://hive-metastore.hive.svc.cluster.local:9083") \
    .enableHiveSupport() \
    .getOrCreate()

# Create views
partition = spark.sql("SELECT date_format(current_date(), 'yyyyMMdd')").collect()[0][0]
spark.sql("DROP VIEW IF EXISTS default.vw_d_customer_feature")
spark.sql("DROP VIEW IF EXISTS default.vw_d_merchant_feature")

spark.sql(f"""
    CREATE OR REPLACE VIEW default.vw_d_customer_feature AS
    SELECT *, current_timestamp() AS event_timestamp
    FROM default.d_customer_feature
    WHERE partition = '{partition}'
""")

spark.sql(f"""
    CREATE OR REPLACE VIEW default.vw_d_merchant_feature AS
    SELECT *, current_timestamp() AS event_timestamp
    FROM default.d_merchant_feature
    WHERE partition = '{partition}'
""")

spark.stop()
