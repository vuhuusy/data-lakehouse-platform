FROM bitnami/spark:3.5.3

USER root

COPY source_code/airflow/dags/spark-jobs/ /opt/spark-jobs/

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r /opt/spark-jobs/requirements.txt && \
    # Clean up pip cache
    rm -rf /root/.cache && rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/*

# Add Spark Kafka connector for Spark 3.5.3
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.3/spark-sql-kafka-0-10_2.12-3.5.3.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.3/spark-token-provider-kafka-0-10_2.12-3.5.3.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar $SPARK_HOME/jars

# Add Delta Lake
ADD https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.3.0/delta-spark_2.12-3.3.0.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/io/delta/delta-storage/3.3.0/delta-storage-3.3.0.jar $SPARK_HOME/jars
# Add AWS jars
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.172/aws-java-sdk-bundle-1.12.172.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.17.257/bundle-2.17.257.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/software/amazon/awssdk/url-connection-client/2.17.257/url-connection-client-2.17.257.jar $SPARK_HOME/jars
# Support for S3 magic committer...
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-hadoop-cloud_2.12/3.3.4/spark-hadoop-cloud_2.12-3.3.4.jar $SPARK_HOME/jars

RUN chmod -R 644 $SPARK_HOME/jars/*

COPY infra/services/kafka/certs/kafka.truststore.jks /opt/spark/secrets/kafka.truststore.jks
COPY infra/services/kafka/certs/kafka.keystore.jks /opt/spark/secrets/kafka.keystore.jks

# Certificate import
COPY infra/services/minio/selfsigned.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates && \
    keytool -importcert -alias minio-ca -file /usr/local/share/ca-certificates/selfsigned.crt \
    -keystore $JAVA_HOME/lib/security/cacerts \
    -storepass changeit -noprompt