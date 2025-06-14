from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
# === Config ===
DELTA_TABLE_PATH = "s3a://gold-zone/fraud_detection/d_customer_feature"
TABLE_NAME = "default.d_customer_feature"
PARTITION_COLUMN = "partition"

# === Date to compact ===
vietnam_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
compact_partition = (vietnam_time - timedelta(days=1)).strftime('%Y%m%d')

# === Init Spark session ===
spark = SparkSession.builder \
    .appName("Compact Delta Partition") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.sql.session.timeZone", "Asia/Ho_Chi_Minh") \
    .config("spark.hadoop.fs.s3a.endpoint", "https://minio.minio.svc.cluster.local:443") \
    .config("spark.hadoop.fs.s3a.access.key", "minio") \
    .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

spark.conf.set("spark.sql.shuffle.partitions", 16)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# === Load data for specific partition ===
df = spark.read.format("delta").load(DELTA_TABLE_PATH) \
    .filter(f"{PARTITION_COLUMN} = '{compact_partition}'")

# === Coalesce to reduce small files ===
df = df.coalesce(4)

# === Overwrite back the same partition ===
df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", f"{PARTITION_COLUMN} = '{compact_partition}'") \
    .option("dataChange", "false") \
    .partitionBy(PARTITION_COLUMN) \
    .save(DELTA_TABLE_PATH)

spark.stop()
