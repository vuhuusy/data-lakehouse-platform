from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

import joblib
import s3fs

####################################################################################################

# Init Spark Session with Delta + S3 support
spark = SparkSession.builder \
    .appName("Calculate Customer and Merchant Features") \
    .config("spark.driver.extraClassPath", "/opt/bitnami/spark/jars/*") \
    .config("spark.executor.extraClassPath", "/opt/bitnami/spark/jars/*") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.session.timeZone", "Asia/Ho_Chi_Minh") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "https://minio.minio.svc.cluster.local:443") \
    .config("spark.hadoop.fs.s3a.access.key", "minio") \
    .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("hive.metastore.uris", "thrift://hive-metastore.hive.svc.cluster.local:9083") \
    .enableHiveSupport() \
    .getOrCreate()

####################################################################################################

# Read Delta tables and Parquet files
merchant = spark.read.format("delta").table("default.merchant")
customer = spark.read.format("delta").table("default.customer")
transaction = spark.read.format("delta").table("default.transaction")
state_features = spark.read.parquet("s3a://gold-zone/features/online_store/state_features.parquet")

####################################################################################################

# Calculate customer features
reference_date = spark.sql("SELECT current_date()").collect()[0][0]

customer = customer \
    .withColumnRenamed('id', 'customer_id') \
    .withColumn('dob', to_date(col('dob').cast('string'), 'yyyy-MM-dd')) \
    .withColumn('age', floor(datediff(lit(reference_date), col('dob')) / 365).cast(IntegerType())) \
    .withColumn('age_group', when(col('age') < 25, '<25')
                .when((col('age') >= 25) & (col('age') < 40), '25–40')
                .when((col('age') >= 40) & (col('age') < 60), '40–60')
                .otherwise('60+')) \
    .withColumn("gender", when(col("gender") == "M", 1).otherwise(0).cast(IntegerType())) \
    .withColumn("is_urban", when(col("area_type") == "urban", 1).otherwise(0).cast(IntegerType())) \
    .withColumn('is_young', (col('age') < 25).cast(IntegerType())) \
    .withColumn('is_elder', (col('age') > 60).cast(IntegerType()))

####################################################################################################

# Connect to MinIO using s3fs
s3 = s3fs.S3FileSystem(anon=False, key='minio', secret='minio123', endpoint_url='https://minio.minio.svc.cluster.local:443',
                       use_ssl=True, client_kwargs={'verify': False})

file_path = 'gold-zone/features/online_store/label_encoders.pkl'
with s3.open(file_path, 'rb') as f:
    le_dict = joblib.load(f)

age_group_mapping = dict(zip(le_dict['age_group'].classes_, le_dict['age_group'].transform(le_dict['age_group'].classes_)))
category_mapping = dict(zip(le_dict['category'].classes_, le_dict['category'].transform(le_dict['category'].classes_)))

def dict_to_map(mapping):
    return create_map([lit(k) for kv in mapping.items() for k in kv])

age_group_map = dict_to_map(age_group_mapping)
category_map = dict_to_map(category_mapping)

####################################################################################################

# Join customer with state features to get state-related features
d_customer = customer.join(broadcast(state_features), customer['state'] == state_features['state_abbreviation'], how='left')

d_customer = d_customer.withColumn("age_group_encoded", age_group_map[col("age_group")]) \
                    .withColumn("age_group_encoded", col("age_group_encoded").cast(IntegerType())) \
                    .withColumn("population_level", col("population_level").cast(IntegerType())) \
                    .withColumn("income_level", col("income_level").cast(IntegerType())) \
                    .withColumn("is_young_state", col("is_young_state").cast(IntegerType()))

d_merchant = merchant.withColumn("category_encoded", category_map[col("category")]) \
                    .withColumnRenamed('id', 'merchant_id') \
                    .withColumn("category_encoded", col("category_encoded").cast(IntegerType()))

####################################################################################################

# Calculate features for transactions (joined with customer info)
txn_last_7d = transaction \
    .withColumn('txn_date', to_date(col('date'), 'yyyy-MM-dd')) \
    .filter(datediff(current_date(), col('txn_date')).between(1, 7)) \
    .join(d_customer, transaction['customer_id'] == d_customer['customer_id'], 'left') \
    .groupBy('transaction.customer_id') \
    .agg(
        count('transaction.id').alias('num_txn_last_7d'),  # Total number of transactions in last 7 days
        avg('amt').alias('avg_amt_last_7d'),   # Average amount of transactions in last 7 days
        sum('amt').alias('sum_amt_last_7d')    # Total sum of transactions in last 7 days
    )

txn_last_7d = txn_last_7d.withColumn('avg_txn_last_7d', col('sum_amt_last_7d') / col('num_txn_last_7d')) \
                    .withColumn('avg_txn_last_7d', col('avg_txn_last_7d').cast(DoubleType())) \
                    .withColumn('sum_amt_last_7d', col('sum_amt_last_7d').cast(DoubleType())) \
                    .withColumn('num_txn_last_7d', col('num_txn_last_7d').cast(DoubleType()))

####################################################################################################

d_customer = d_customer \
    .join(txn_last_7d, 'customer_id', 'left')

partition = spark.sql("SELECT date_format(current_date(), 'yyyyMMdd')").collect()[0][0]
d_merchant = d_merchant.withColumn('partition', lit(partition))
d_customer = d_customer.withColumn('partition', lit(partition))

d_customer = d_customer.fillna(0)
d_merchant = d_merchant.fillna(0)

####################################################################################################

# Create Delta tables if not exist
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS default.d_merchant_feature (
        merchant_id STRING,
        category_encoded INT,
        partition STRING
    )
    USING DELTA
    PARTITIONED BY (partition)
    LOCATION 's3a://gold-zone/fraud_detection/d_merchant_feature'
""")

spark.sql(f"""
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

####################################################################################################

# Write the transformed data to Delta tables
d_merchant.select('merchant_id', 'category_encoded', 'partition') \
    .coalesce(2) \
    .write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("partition") \
    .saveAsTable("default.d_merchant_feature")

d_customer.select(
    'customer_id', 'age', 'age_group_encoded', 'is_young', 'is_elder', 'gender', 'city', 'state', 'lat', 'lon',
    'is_urban', 'population_level', 'income_level', 'is_young_state', 'norm_poverty_rate', 'norm_unemployment_rate',
    'norm_poverty_per_unemployed', 'avg_txn_last_7d', 'avg_amt_last_7d', 'sum_amt_last_7d', 'num_txn_last_7d',
    'partition'
)   \
    .coalesce(8) \
    .write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("partition") \
    .saveAsTable("default.d_customer_feature")

####################################################################################################

# Stop the Spark session
spark.stop()