from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType

import joblib


# Init Spark Session with Delta + S3 support
spark = SparkSession.builder \
    .appName("Calculate Customer and Merchant Features") \
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

# Read Delta tables and Parquet files
merchant = spark.read.format("delta").table("default.merchant")
customer = spark.read.format("delta").table("default.customer")
transaction = spark.read.format("delta").table("default.transaction")
state_features = spark.read.parquet("s3a://gold-zone/features/online_store/state_features.parquet")

# Calculate customer features
customer = customer.withColumn('dob', to_date(col('dob').cast('string'), 'yyyy-MM-dd'))

reference_date = spark.sql("SELECT current_date()").collect()[0][0]

customer = customer.withColumn('age', floor(datediff(lit(reference_date), col('dob')) / 365).cast(IntegerType()))

customer = customer.withColumn('age_group', when(col('age') < 25, '<25')
                                    .when((col('age') >= 25) & (col('age') < 40), '25–40')
                                    .when((col('age') >= 40) & (col('age') < 60), '40–60')
                                    .otherwise('60+'))


import joblib
import pyarrow.fs as fs
import s3fs

# Kết nối với MinIO thông qua s3fs hoặc pyarrow
s3 = s3fs.S3FileSystem(anon=False, key='minio', secret='minio123', endpoint_url='https://minio.minio.svc.cluster.local:443')

# Đường dẫn đến file trên MinIO
file_path = 'gold-zone/features/online_store/label_encoders.pkl'

# Đọc tệp pickle trực tiếp từ MinIO sử dụng pyarrow và joblib
with s3.open(file_path, 'rb') as f:
    le_dict = joblib.load(f)

# Kiểm tra các encoder đã tải
print(le_dict)

# UDF to apply label encoding
def label_encoding(feature_name, value):
    encoder = le_dict.get(feature_name)
    if encoder:
        return encoder.transform([value])[0]
    else:
        return None

apply_label_encoding_udf = udf(label_encoding, IntegerType())

customer = customer.withColumn("age_group_encoded", apply_label_encoding_udf(lit("age_group"), col("age_group")))

merchant = merchant.withColumn("category_encoded", apply_label_encoding_udf(lit("category"), col("category")))

d_customer = customer.join(state_features, customer['state'] == state_features['state_abbreviation'], how='left')



d_customer.select('*').show()
merchant.select('*').show()



# Stop Spark session
spark.stop()