FROM flink:16

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

RUN apt-get update -y && \
apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libffi-dev && \
wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz && \
tar -xvf Python-3.7.9.tgz && \
cd Python-3.7.9 && \
./configure --without-tests --enable-shared && \
make -j6 && \
make install && \
ldconfig /usr/local/lib && \
cd .. && rm -f Python-3.7.9.tgz && rm -rf Python-3.7.9 && \
ln -s /usr/local/bin/python3 /usr/local/bin/python && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

RUN pip3 install "apache-flink>=1.16.0,<1.17.1"

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