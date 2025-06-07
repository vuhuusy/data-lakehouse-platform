from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig, RollingPolicy
from pyflink.common import Duration
from java.util import Properties

env = StreamExecutionEnvironment.get_execution_environment()

# Kafka settings
props = Properties()
props.setProperty("bootstrap.servers", "kafka.kafka.svc.cluster.local:9093")
props.setProperty("group.id", "flink-group")
props.setProperty("security.protocol", "SASL_SSL")
props.setProperty("sasl.mechanism", "PLAIN")
props.setProperty("ssl.truststore.location", "/opt/flink/secrets/kafka.truststore.jks")
props.setProperty("ssl.truststore.password", "changeit")
props.setProperty("sasl.jaas.config", 'org.apache.kafka.common.security.plain.PlainLoginModule required username="kafka" password="kafka";')

consumer = FlinkKafkaConsumer(
    topics='financial-ops.core.transaction',
    deserialization_schema=SimpleStringSchema(),
    properties=props
)

# # Sink to MinIO
# sink = FileSink.for_row_format(
#     "s3a://work-zone/transactions/",
#     SimpleStringSchema()
# ).with_rolling_policy(
#     RollingPolicy.default_rolling_policy(Duration.of_minutes(15), Duration.of_minutes(5), 128 * 1024)
# ).with_output_file_config(
#     OutputFileConfig.builder().with_part_prefix("part").with_part_suffix(".txt").build()
# ).build()

# stream = env.add_source(consumer)
# stream.sink_to(sink)

# env.execute("Kafka to MinIO Sink Job")
