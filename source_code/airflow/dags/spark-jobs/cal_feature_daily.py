from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, sum, lit, udf
from pyspark.sql.types import IntegerType
import json
from datetime import datetime, timedelta

# ========================
# 🕒 1. Get dynamic date range
# ========================
today = datetime.now().date()
start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
today_str = today.strftime("%Y-%m-%d")

# ========================
# 🚀 2. Spark session
# ========================
spark = SparkSession.builder \
    .appName("FeatureCalculationJobDaily") \
    .config("spark.hadoop.fs.s3a.endpoint", "https://minio.minio.svc.cluster.local:443") \
    .config("spark.hadoop.fs.s3a.access.key", "minio") \
    .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# ========================
# 📥 3. Read raw transactions
# ========================
df = spark.read.parquet("s3a://raw-data/transaction/")

window_df = df.filter((col("event_date") >= start_date) & (col("event_date") <= end_date))

# ========================
# 📊 4. Aggregation
# ========================
agg = window_df.groupBy("customer_id").agg(
    count("*").alias("num_txn_last_7d"),
    avg("amt").alias("avg_amt_last_7d"),
    sum("amt").alias("sum_amt_last_7d"),
    avg("lat").alias("home_lat"),
    avg("lon").alias("home_lon")
)

# ========================
# 👤 5. Enrich with customer profile
# ========================
profile = spark.read.parquet("s3a://master_data/customer_profile/")
agg = agg.join(profile, on="customer_id", how="left")

# ========================
# 🏷️ 6. Label encoding
# ========================
def load_mapping(file):
    with open(file) as f:
        return json.load(f)

def label_encode(mapping):
    def encode_fn(value):
        return int(mapping.get(str(value), -1))
    return udf(encode_fn, IntegerType())

age_map = load_mapping("mapping/age_group.json")
group_map = load_mapping("mapping/group.json")
mcc_map = load_mapping("mapping/merchant_category.json")

agg = agg.withColumn("age_group_encoded", label_encode(age_map)("age_group")) \
         .withColumn("group_encoded", label_encode(group_map)("group")) \
         .withColumn("merchant_category_encoded", label_encode(mcc_map)("merchant_category"))

# ========================
# 📝 7. Add partition date
# ========================
agg = agg.withColumn("event_date", lit(today_str))

# ========================
# 💾 8. Save to MinIO
# ========================
agg.write.partitionBy("event_date") \
    .mode("overwrite") \
    .parquet("s3a://features/customer_features/")

print(f"✅ Feature generation completed for date: {today_str}")
