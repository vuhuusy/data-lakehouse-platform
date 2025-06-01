from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

# 1️⃣ Init Spark Session with Delta + S3 support
spark = SparkSession.builder \
    .appName("KafkaToDelta") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "https://minio.minio.svc.cluster.local:443") \
    .config("spark.hadoop.fs.s3a.access.key", "minio") \
    .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# 2️⃣ Kafka and Delta config
KAFKA_BOOTSTRAP = "kafka.kafka.svc.cluster.local:9092"
TOPIC = "financial-ops.core.merchant"
DELTA_PATH = "s3a://raw-zone/delta/merchant"
CHECKPOINT_PATH = "s3a://raw-zone/checkpoints/merchant"  # ✅ đã đúng – tách riêng checkpoint khỏi dữ liệu

# 3️⃣ Define schema of Kafka message
after_schema = StructType([
    StructField("id", StringType()),
    StructField("name", StringType()),
    StructField("category", StringType())
])

envelope_schema = StructType([
    StructField("after", after_schema)
])

# 4️⃣ Read from Kafka (secure)
df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "latest") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanism", "SCRAM-SHA-256") \
    .option("kafka.sasl.jaas.config",
            "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"kafka\" password=\"kafka\";") \
    .option("kafka.ssl.truststore.location", "/opt/spark/secrets/kafka.truststore.jks") \
    .option("kafka.ssl.truststore.password", "changeit") \
    .option("kafka.ssl.truststore.type", "JKS") \
    .option("kafka.ssl.keystore.location", "/opt/spark/secrets/kafka.keystore.jks") \
    .option("kafka.ssl.keystore.password", "changeit") \
    .option("kafka.ssl.keystore.type", "JKS") \
    .load()

# 5️⃣ Parse JSON message
df_after = df_kafka.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), envelope_schema).alias("data")) \
    .select("data.after.*") \
    .where("id IS NOT NULL")

# 6️⃣ Write to Delta on MinIO
df_after.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", CHECKPOINT_PATH) \
    .start(DELTA_PATH) \
    .awaitTermination()
