FROM flink:1.17

USER root

ARG PYTHON_VERSION=3.9.18
ARG FLINK_VERSION=1.17.2

ENV PYTHON_VERSION=${PYTHON_VERSION}
ENV FLINK_VERSION=${FLINK_VERSION}

# Download connector libs
ADD https://repo.maven.apache.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar /opt/flink/lib/
ADD https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/${FLINK_VERSION}/flink-sql-connector-kafka-${FLINK_VERSION}.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-hdfs/3.3.4/hadoop-hdfs-3.3.4.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.172/aws-java-sdk-bundle-1.12.172.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-s3-fs-hadoop/1.17.0/flink-s3-fs-hadoop-1.17.0.jar /opt/flink/lib/
ADD https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.1.0-1.17/flink-connector-kafka-3.1.0-1.17.jar /opt/flink/lib/

COPY infra/certs/minio/selfsigned.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates && \
    keytool -importcert -alias minio-ca -file /usr/local/share/ca-certificates/selfsigned.crt \
    -keystore "${JAVA_HOME}/lib/security/cacerts" \
    -storepass changeit -noprompt

COPY infra/certs/kafka/kafka.truststore.jks /opt/flink/secrets/kafka.truststore.jks
COPY infra/certs/kafka/kafka.keystore.jks /opt/flink/secrets/kafka.keystore.jks

RUN chmod -R 644 /opt/flink/lib/*.jar && \
    chmod 600 /opt/flink/secrets/kafka.truststore.jks && \
    chmod 600 /opt/flink/secrets/kafka.keystore.jks

# Install Python
RUN apt-get update -y && \
  apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libpq-dev \
    wget \
    curl \
    ca-certificates && \
  wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
  tar -xvf Python-${PYTHON_VERSION}.tgz && \
  cd Python-${PYTHON_VERSION} && \
  ./configure --without-tests --enable-shared && \
  make -j6 && \
  make install && \
  ldconfig /usr/local/lib && \
  cd .. && rm -f Python-${PYTHON_VERSION}.tgz && rm -rf Python-${PYTHON_VERSION} && \
  ln -s /usr/local/bin/python3 /usr/local/bin/python && \
  python3 -m ensurepip && \
  python3 -m pip install --upgrade pip && \
  python3 -m pip install --no-cache-dir requests aiohttp && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Install pip packages
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir apache-flink==${FLINK_VERSION} && \
    python3 -m pip install --upgrade "pip<24.1" && \
    python3 -m pip install --no-cache-dir \
      "feast==0.16.1" \
      "pydantic==1.10.13" \
      "click<8.1" \
      "regex" \
      "pandas" \
      "feast[redis]" \
      "feast[aws]" \
      "git+https://github.com/shopify/feast-trino.git@main"

RUN pip uninstall protobuf -y
RUN pip install protobuf==3.20.3

# Add Python script and feature repo
USER flink
RUN mkdir -p /opt/flink/usrlib
COPY script/airflow/feature_store/fraud_detection/feature_repo/ /opt/flink/feature_store/
ADD infra/services/flink/flink-job.py /opt/flink/usrlib/flink-job.py

WORKDIR /opt/flink/feature_store
