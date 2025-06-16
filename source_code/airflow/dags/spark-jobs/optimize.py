from pyspark.sql import SparkSession
from delta.tables import DeltaTable

# === Init Spark ===
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

# === Get partition N-1 (Vietnam time) ===
partition = spark.sql("""
    SELECT DATE_FORMAT(CURRENT_DATE(), 'yyyyMMdd') AS partition
""").collect()[0]['partition']
print(f">>> 🕒 Optimizing partition = {partition}")

spark.sql(f"""
OPTIMIZE delta.`s3a://gold-zone/f_transaction_predictions`
WHERE partition = '{partition}'
""")
