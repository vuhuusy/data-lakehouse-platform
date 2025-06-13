from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import joblib, s3fs

# Initialize Spark session
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

# Broadcast state features to all nodes
state_features = broadcast(state_features)

# Calculate customer features
customer = customer \
    .withColumnRenamed('id', 'customer_id') \
    .withColumn('dob', to_date(col('dob').cast('string'), 'yyyy-MM-dd')) \
    .withColumn('age', floor(datediff(current_date(), col('dob')) / 365)) \
    .withColumn('age_group', when(col('age') < 25, '<25')
                .when((col('age') < 40), '25–40')
                .when((col('age') < 60), '40–60')
                .otherwise('60+')) \
    .withColumn("gender", when(col("gender") == "M", 1).otherwise(0)) \
    .withColumn("is_urban", when(col("area_type") == "urban", 1).otherwise(0)) \
    .withColumn('is_young', (col('age') < 25).cast(IntegerType())) \
    .withColumn('is_elder', (col('age') > 60).cast(IntegerType()))

# Load label encoders
s3 = s3fs.S3FileSystem(anon=False, key='minio', secret='minio123',
                       endpoint_url='https://minio.minio.svc.cluster.local:443',
                       use_ssl=True, client_kwargs={'verify': False})
file_path = 'gold-zone/features/online_store/label_encoders.pkl'
with s3.open(file_path, 'rb') as f:
    le_dict = joblib.load(f)

def dict_to_map(mapping):
    return create_map([lit(k) for kv in mapping.items() for k in kv])

age_group_map = dict_to_map(dict(zip(le_dict['age_group'].classes_,
                                     le_dict['age_group'].transform(le_dict['age_group'].classes_))))
category_map = dict_to_map(dict(zip(le_dict['category'].classes_,
                                    le_dict['category'].transform(le_dict['category'].classes_))))

# Join + encode
d_customer = customer.join(state_features, customer['state'] == state_features['state_abbreviation'], 'left') \
    .withColumn("age_group_encoded", age_group_map[col("age_group")].cast(IntegerType())) \
    .withColumn("population_level", col("population_level").cast(IntegerType())) \
    .withColumn("income_level", col("income_level").cast(IntegerType())) \
    .withColumn("is_young_state", col("is_young_state").cast(IntegerType()))

d_merchant = merchant \
    .withColumn("category_encoded", category_map[col("category")].cast(IntegerType())) \
    .withColumnRenamed('id', 'merchant_id')

# Calculate transaction features
txn_last_7d = transaction \
    .withColumn('txn_date', to_date(col('date'), 'yyyy-MM-dd')) \
    .filter(datediff(current_date(), col('txn_date')).between(1, 7)) \
    .groupBy('customer_id') \
    .agg(
        count('*').alias('num_txn_last_7d'),
        avg('amt').alias('avg_amt_last_7d'),
        sum('amt').alias('sum_amt_last_7d')
    ) \
    .withColumn('avg_txn_last_7d', col('sum_amt_last_7d') / col('num_txn_last_7d')) \
    .selectExpr("customer_id", 
                "CAST(num_txn_last_7d AS DOUBLE)",
                "CAST(avg_amt_last_7d AS DOUBLE)",
                "CAST(sum_amt_last_7d AS DOUBLE)",
                "CAST(avg_txn_last_7d AS DOUBLE)")

# Join transaction features with customer features
d_customer = d_customer.join(txn_last_7d, 'customer_id', 'left') \
    .fillna(0)

# Add partition column
partition = spark.sql("SELECT date_format(current_date(), 'yyyyMMdd')").collect()[0][0]
d_customer = d_customer.withColumn('partition', lit(partition))
d_merchant = d_merchant.withColumn('partition', lit(partition))

# Create Delta tables if not exists
spark.sql("""
    CREATE TABLE IF NOT EXISTS default.d_customer_feature (
        customer_id STRING,
        age INT,
        age_group_encoded INT,
        is_young INT,
        is_elder INT,
        gender INT,
        city STRING,
        state STRING,
        lat DOUBLE,
        lon DOUBLE,
        is_urban INT,
        population_level INT,
        income_level INT,
        is_young_state INT,
        norm_poverty_rate DOUBLE,
        norm_unemployment_rate DOUBLE,
        norm_poverty_per_unemployed DOUBLE,
        avg_txn_last_7d DOUBLE,
        avg_amt_last_7d DOUBLE,
        sum_amt_last_7d DOUBLE,
        num_txn_last_7d DOUBLE,
        partition STRING
    )
    USING DELTA
    PARTITIONED BY (partition)
    LOCATION 's3a://gold-zone/fraud_detection/d_customer_feature'
""")

spark.sql("""
    CREATE TABLE IF NOT EXISTS default.d_merchant_feature (
        merchant_id STRING,
        category_encoded INT,
        partition STRING
    )
    USING DELTA
    PARTITIONED BY (partition)
    LOCATION 's3a://gold-zone/fraud_detection/d_merchant_feature'
""")

# Write to Delta tables
d_customer.coalesce(8).write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("partition") \
    .saveAsTable("default.d_customer_feature")

d_merchant.coalesce(2).write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("partition") \
    .saveAsTable("default.d_merchant_feature")

spark.stop()
