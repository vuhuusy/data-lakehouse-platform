from datetime import datetime, timedelta
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

# === Spark tuning ===
spark.conf.set("spark.sql.shuffle.partitions", 8)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")  # allow vacuum 0h
spark.sql("SET spark.databricks.delta.optimizeWrite.enabled = true")
spark.sql("SET spark.databricks.delta.autoCompact.enabled = true")

# === Get partition N-1 (Vietnam time) ===
compact_partition = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
print(f">>> 🕒 Processing partition = {compact_partition}")

# === Table info: {table_name: coalesce_num}
tables = {
    "default.transaction": 16,
    "default.d_customer_feature": 4,
    "default.d_merchant_feature": 2,
    "default.f_transaction_predictions": 16,
}

# === Process each table ===
for table, coalesce_num in tables.items():
    print(f"\n>>> Compacting table: {table} | partition={compact_partition}")
    try:
        df = spark.table(table).filter(f"partition = '{compact_partition}'").coalesce(coalesce_num)

        df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("replaceWhere", f"partition = '{compact_partition}'") \
            .partitionBy("partition") \
            .saveAsTable(table)

        print(f">>> ✅ Compacted: {table} into {coalesce_num} file(s)")

        print(f">>> 🧹 Running vacuum on {table} ...")
        delta_table = DeltaTable.forName(spark, table)
        delta_table.vacuum(0)
        print(f">>> ✅ Vacuumed: {table}")

    except Exception as e:
        print(f">>> ❌ Error processing table {table}: {e}")

spark.stop()
