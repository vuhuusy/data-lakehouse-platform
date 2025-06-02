from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_date, date_format
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, FloatType

# Init SparkSession with Delta + S3 support
spark = SparkSession.builder \
    .appName("CDC-Transaction") \
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

# Define schema for transaction
transaction_after_schema = StructType([
    StructField("id", StringType()),
    StructField("date", StringType()),
    StructField("time", StringType()),
    StructField("amt", FloatType()),
    StructField("lat", FloatType()),
    StructField("lon", FloatType()),
    StructField("customer_id", StringType()),
    StructField("merchant_id", StringType())
])

transaction_envelope_schema = StructType([
    StructField("after", transaction_after_schema)
])

# Kafka Configs
KAFKA_BOOTSTRAP = "kafka.kafka.svc.cluster.local:9092"
TOPIC = "financial-ops.core.transaction"
DELTA_PATH = "s3a://raw-zone/transaction"
CHECKPOINT_PATH = "s3a://work-zone/spark/checkpoints/transaction"
TABLE_NAME = "transaction"
DATABASE_NAME = "default"

# Read from Kafka
df_transaction = spark.readStream \
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
    .option("kafka.ssl.truststore.type", "JKS") \
    .option("kafka.ssl.keystore.location", "/opt/spark/secrets/kafka.keystore.jks") \
    .option("kafka.ssl.keystore.password", "changeit") \
    .option("kafka.ssl.keystore.type", "JKS") \
    .load()

# Parse & transform
transaction = df_transaction.selectExpr("CAST(value AS STRING) AS json") \
    .select(from_json(col("json"), transaction_envelope_schema).alias("data")) \
    .select("data.after.*") \
    .where("id IS NOT NULL") \
    .withColumn("partition", date_format(to_date(col("date"), "yyyy-MM-dd"), "yyyyMMdd"))

# Ensure database exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")

# Create Delta table if not exists
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {DATABASE_NAME}.{TABLE_NAME} (
        id STRING,
        date STRING,
        time STRING,
        amt DOUBLE,
        lat FLOAT,
        lon FLOAT,
        customer_id STRING,
        merchant_id STRING,
        partition STRING
    )
    USING DELTA
    PARTITIONED BY (partition)
    LOCATION '{DELTA_PATH}'
""")

# Write to Delta
query = transaction.writeStream \
    .format("delta") \
    .outputMode("append") \
    .partitionBy("partition") \
    .option("checkpointLocation", CHECKPOINT_PATH) \
    .start(DELTA_PATH)

query.awaitTermination()
