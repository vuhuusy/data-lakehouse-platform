from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Read State Features from MinIO") \
    .getOrCreate()

# MinIO S3 URL (s3a://bucket/path)
df = spark.read.parquet("s3a://gold-zone/features/online_store/state_features.parquet")

df.show(5, truncate=False)

spark.stop()
