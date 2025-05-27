from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp

spark = SparkSession.builder \
    .appName("StreamToMinIO") \
    .getOrCreate()

df_stream = spark.readStream.format("rate").option("rowsPerSecond", 10).load()

df_transformed = df_stream.withColumn("ingest_time", current_timestamp())

query = df_transformed.writeStream \
    .format("parquet") \
    .option("path", "s3a://gold-zone/streamed_output/") \
    .option("checkpointLocation", "s3a://gold-zone/streamed_output/_checkpoints/") \
    .outputMode("append") \
    .start()

query.awaitTermination()
