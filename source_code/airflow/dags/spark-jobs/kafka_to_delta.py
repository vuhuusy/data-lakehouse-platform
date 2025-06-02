from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

# 1️⃣ Init Spark Session with Delta + S3 support
spark = SparkSession.builder \
    .appName("KafkaToDelta") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3,"
            "org.apache.kafka:kafka-clients:3.4.0,"
            "io.delta:delta-core_2.12:2.4.0,"
            "org.apache.commons:commons-pool2:2.11.1") \
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

after_schema = StructType([
    StructField("id", StringType()),
    StructField("ssn", StringType()),
    StructField("cc_num", StringType()),
    StructField("first", StringType()),
    StructField("last", StringType()),
    StructField("gender", StringType()),
    StructField("street", StringType()),
    StructField("city", StringType()),
    StructField("state", StringType()),
    StructField("zip", StringType()),
    StructField("lat", DoubleType()),
    StructField("long", DoubleType()),
    StructField("job", StringType()),
    StructField("dob", LongType()),
    StructField("acct_num", StringType()),
    StructField("area_type", StringType())
])

envelope_schema = StructType([
    StructField("after", after_schema)
])

KAFKA_BOOTSTRAP = "kafka.kafka.svc.cluster.local:9092"
TOPIC = "financial-ops.core.customer"
DELTA_PATH = "s3a://raw-zone/delta/customer"
CHECKPOINT_PATH = "s3a://raw-zone/checkpoints/customer"
TABLE_NAME = "customer"
DATABASE_NAME = "default"

df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "earliest") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanism", "SCRAM-SHA-256") \
    .option("kafka.sasl.jaas.config",
            'org.apache.kafka.common.security.scram.ScramLoginModule required username="kafka" password="kafka";') \
    .option("kafka.ssl.truststore.location", "/opt/spark/secrets/kafka.truststore.jks") \
    .option("kafka.ssl.truststore.password", "changeit") \
    .option("kafka.ssl.truststore.type", "JKS") \
    .option("kafka.ssl.keystore.location", "/opt/spark/secrets/kafka.keystore.jks") \
    .option("kafka.ssl.keystore.password", "changeit") \
    .option("kafka.ssl.keystore.type", "JKS") \
    .load()

df_after = df_kafka.selectExpr("CAST(value AS STRING) AS json") \
    .select(from_json(col("json"), envelope_schema).alias("data")) \
    .select("data.after.*") \
    .where("id IS NOT NULL")

spark.sql("CREATE DATABASE IF NOT EXISTS default").show()

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {DATABASE_NAME}.{TABLE_NAME} (
        id STRING,
        ssn STRING,
        cc_num STRING,
        first STRING,
        last STRING,
        gender STRING,
        street STRING,
        city STRING,
        state STRING,
        zip STRING,
        lat DOUBLE,
        long DOUBLE,
        job STRING,
        dob BIGINT,
        acct_num STRING,
        area_type STRING
    )
    USING DELTA
    LOCATION '{DELTA_PATH}'
""")

query = df_after.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", CHECKPOINT_PATH) \
    .start(DELTA_PATH)

query.awaitTermination()
