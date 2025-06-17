FROM apache/airflow:2.10.5
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

COPY infra/services/airflow/requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt