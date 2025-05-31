FROM flink:1.20.0-java11

USER root

# Thêm thư viện hỗ trợ S3 (MinIO) & Kafka connector
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-hdfs/3.3.4/hadoop-hdfs-3.3.4.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.172/aws-java-sdk-bundle-1.12.172.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-s3-fs-hadoop/1.20.0/flink-s3-fs-hadoop-1.20.0.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.4.0-1.20/flink-connector-kafka-3.4.0-1.20.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar /opt/flink/lib/

# Import CA certificate để tin cậy MinIO tự ký (nếu có)
COPY infra/services/minio/selfsigned.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates && \
    keytool -importcert -alias minio-ca -file /usr/local/share/ca-certificates/selfsigned.crt \
    -keystore "${JAVA_HOME}/lib/security/cacerts" \
    -storepass changeit -noprompt

# Thêm truststore Kafka nếu cần SSL xác thực
COPY infra/services/kafka/certs/kafka.truststore.jks /opt/flink/secrets/kafka.truststore.jks

# Set permission an toàn
RUN chmod -R 644 /opt/flink/lib/*.jar && \
    chmod 600 /opt/flink/secrets/kafka.truststore.jks

USER flink
