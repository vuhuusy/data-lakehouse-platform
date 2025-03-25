FROM apache/nifi:1.23.2

COPY infra/services/minio/selfsigned.crt /usr/local/share/ca-certificates/selfsigned.crt

USER root
RUN update-ca-certificates
RUN keytool -importcert -alias minio-ca \
    -file /usr/local/share/ca-certificates/selfsigned.crt \
    -keystore $JAVA_HOME/lib/security/cacerts \
    -storepass changeit -noprompt

USER nifi