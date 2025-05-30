FROM flink:1.20-scala_2.12

USER root

# Add jars
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.172/aws-java-sdk-bundle-1.12.172.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-s3-fs-hadoop/1.20.0/flink-s3-fs-hadoop-1.20.0.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-hdfs/3.3.4/hadoop-hdfs-3.3.4.jar /opt/flink/lib/

# Kafka connector for Flink
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.4.0-1.20/flink-connector-kafka-3.4.0-1.20.jar /opt/flink/lib/


WORKDIR /opt/flink/workdir

RUN apt-get update && \
    apt-get install -y curl python3 python3-pip && \
    pip3 install --upgrade pip setuptools && \
    rm -rf /var/lib/apt/lists/*

# Certificate import
COPY infra/services/minio/selfsigned.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates && \
    keytool -importcert -alias minio-ca -file /usr/local/share/ca-certificates/selfsigned.crt \
    -keystore $JAVA_HOME/lib/security/cacerts \
    -storepass changeit -noprompt

# Copy Kafka truststore
COPY infra/services/kafka/certs/kafka.truststore.jks /opt/flink/secrets/kafka.truststore.jks

RUN chmod -R 644 /opt/flink/lib/*.jar

USER flink