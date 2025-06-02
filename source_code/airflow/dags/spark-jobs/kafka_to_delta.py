from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

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
    .config("hive.metastore.uris", "thrift://hive-metastore.data-platform.svc.cluster.local:9083") \
    .enableHiveSupport() \
    .getOrCreate()

table_name = "transaction"  # Choose your table name
database_name = "default" # Choose your database name. Default is used if you don't specify one.

spark.sql("CREATE DATABASE IF NOT EXISTS default").show()

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {database_name}.{table_name} (country STRING, continent STRING) USING delta
""")

spark.sql(f"""
  INSERT INTO {database_name}.{table_name} VALUES
      ('china', 'asia'),
      ('argentina', 'south america')
""")

# Show all tables in the default database
spark.sql("SHOW TABLES").show()

# Show all tables in a specific database:
spark.sql(f"SHOW TABLES IN {database_name}").show()

# Show tables with a specific pattern (e.g., all tables starting with "tra"):
spark.sql("SHOW TABLES LIKE 'tra*'").show()

# Describe the table schema
spark.sql(f"DESCRIBE {database_name}.{table_name}").show()

# Query the data from the Hive table
spark.sql(f"SELECT * FROM {database_name}.{table_name}").show()

# Stop the Spark session
spark.stop()

# # 2️⃣ Kafka and Delta config
# KAFKA_BOOTSTRAP = "kafka.kafka.svc.cluster.local:9092"
# TOPIC = "financial-ops.core.merchant"
# DELTA_PATH = "s3a://raw-zone/delta/merchant"
# CHECKPOINT_PATH = "s3a://raw-zone/checkpoints/merchant"

# # 3️⃣ Define correct schema for Debezium envelope
# envelope_schema = StructType([
#     StructField("payload", StructType([
#         StructField("after", StructType([
#             StructField("id", StringType()),
#             StructField("name", StringType()),
#             StructField("category", StringType())
#         ]))
#     ]))
# ])

# # 4️⃣ Read from Kafka
# df_kafka = spark.readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
#     .option("subscribe", TOPIC) \
#     .option("startingOffsets", "earliest") \
#     .option("kafka.security.protocol", "SASL_SSL") \
#     .option("kafka.sasl.mechanism", "SCRAM-SHA-256") \
#     .option("kafka.sasl.jaas.config",
#             "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"kafka\" password=\"kafka\";") \
#     .option("kafka.ssl.truststore.location", "/opt/spark/secrets/kafka.truststore.jks") \
#     .option("kafka.ssl.truststore.password", "changeit") \
#     .option("kafka.ssl.truststore.type", "JKS") \
#     .option("kafka.ssl.keystore.location", "/opt/spark/secrets/kafka.keystore.jks") \
#     .option("kafka.ssl.keystore.password", "changeit") \
#     .option("kafka.ssl.keystore.type", "JKS") \
#     .load()

# # 5️⃣ Parse Debezium JSON and extract after.*
# df_after = df_kafka.selectExpr("CAST(value AS STRING) as json") \
#     .select(from_json(col("json"), envelope_schema).alias("data")) \
#     .select("data.payload.after.*") \
#     .where("id IS NOT NULL")

# # 6️⃣ Create or replace Delta table schema (only once)
# spark.sql(f"""
#     CREATE TABLE IF NOT EXISTS merchant_delta (
#         id STRING,
#         name STRING,
#         category STRING
#     )
#     USING DELTA
#     LOCATION '{DELTA_PATH}'
# """)

# # 7️⃣ Stream write to Delta + keep schema in metastore
# query = df_after.writeStream \
#     .format("delta") \
#     .outputMode("append") \
#     .option("checkpointLocation", CHECKPOINT_PATH) \
#     .start(DELTA_PATH)

# query.awaitTermination()
