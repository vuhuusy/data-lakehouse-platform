from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_date, date_format
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType

# Init Spark Session with Delta + S3 support
spark = SparkSession.builder \
    .appName("Predicted-Transaction") \
    .config("spark.driver.extraClassPath", "/opt/bitnami/spark/jars/*") \
    .config("spark.executor.extraClassPath", "/opt/bitnami/spark/jars/*") \
    .config("spark.sql.shuffle.partitions", "5") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "https://minio.minio.svc.cluster.local:443") \
    .config("spark.hadoop.fs.s3a.access.key", "minio") \
    .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("hive.metastore.uris", "thrift://hive-metastore.hive.svc.cluster.local:9083") \
    .enableHiveSupport() \
    .getOrCreate()

# Define the schema for the Kafka messages
predicted_schema = StructType([
    StructField("id", StringType()),
    StructField("date", StringType()),
    StructField("time", StringType()),
    StructField("amt", FloatType()),
    StructField("lat", FloatType()),
    StructField("lon", FloatType()),
    StructField("customer_id", StringType()),
    StructField("merchant_id", StringType()),
    StructField("norm_poverty_rate", FloatType()),
    StructField("sum_amt_last_7d", FloatType()),
    StructField("gender", IntegerType()),
    StructField("avg_txn_last_7d", FloatType()),
    StructField("norm_unemployment_rate", FloatType()),
    StructField("is_young", IntegerType()),
    StructField("age", IntegerType()),
    StructField("is_urban", IntegerType()),
    StructField("is_elder", IntegerType()),
    StructField("population_level", IntegerType()),
    StructField("is_young_state", IntegerType()),
    StructField("norm_poverty_per_unemployed", FloatType()),
    StructField("avg_amt_last_7d", FloatType()),
    StructField("category_encoded", IntegerType()),
    StructField("age_group_encoded", IntegerType()),
    StructField("num_txn_last_7d", IntegerType()),
    StructField("income_level", IntegerType()),
    StructField("hour", IntegerType()),
    StructField("dayofweek", IntegerType()),
    StructField("month", IntegerType()),
    StructField("is_night", IntegerType()),
    StructField("is_weekend", IntegerType()),
    StructField("is_peak_hour", IntegerType()),
    StructField("log_amt", FloatType()),
    StructField("is_high_amt", IntegerType()),
    StructField("distance_from_home", FloatType()),
    StructField("is_far_from_home", IntegerType()),
    StructField("num_txn_last_2h", IntegerType()),
    StructField("time_diff", FloatType()),
    StructField("is_first_txn", IntegerType()),
    StructField("is_amt_surge", IntegerType()),
    StructField("is_fraud", IntegerType())
])

# Cấu hình
KAFKA_BOOTSTRAP = "kafka.kafka.svc.cluster.local:9092"
TOPIC = "predicted-transaction"
DELTA_PATH = "s3a://gold-zone/f_transaction_predictions"
CHECKPOINT_PATH = "s3a://work-zone/spark/checkpoints/f_transaction_predictions"
TABLE_NAME = "f_transaction_predictions"
DATABASE_NAME = "default"

# Đọc từ Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "earliest") \
    .option("maxOffsetsPerTrigger", 1000) \
    .option("failOnDataLoss", "false") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanism", "SCRAM-SHA-256") \
    .option("kafka.sasl.jaas.config", 'org.apache.kafka.common.security.scram.ScramLoginModule required username="kafka" password="kafka";') \
    .option("kafka.ssl.truststore.location", "/opt/spark/secrets/kafka.truststore.jks") \
    .option("kafka.ssl.truststore.password", "changeit") \
    .option("kafka.ssl.keystore.location", "/opt/spark/secrets/kafka.keystore.jks") \
    .option("kafka.ssl.keystore.password", "changeit") \
    .load()

# Parse JSON
parsed = df.selectExpr("CAST(value AS STRING) AS json") \
    .select(from_json(col("json"), predicted_schema).alias("data")) \
    .select("data.*") \
    .withColumn("partition", date_format(to_date(col("date"), "yyyy-MM-dd"), "yyyyMMdd"))

# Đảm bảo DB tồn tại
spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")

# Tạo bảng Delta nếu chưa có
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {DATABASE_NAME}.{TABLE_NAME} (
        {', '.join([f"{f.name} {f.dataType.simpleString()}" for f in predicted_schema.fields])},
        partition STRING
    )
    USING DELTA
    PARTITIONED BY (partition)
    LOCATION '{DELTA_PATH}'
""")

# Ghi stream
parsed.coalesce(3) \
    .writeStream \
    .format("delta") \
    .outputMode("append") \
    .partitionBy("partition") \
    .option("checkpointLocation", CHECKPOINT_PATH) \
    .trigger(processingTime="10 seconds") \
    .start(DELTA_PATH) \
    .awaitTermination()
