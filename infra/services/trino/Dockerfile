FROM trinodb/trino:470

COPY infra/services/minio/selfsigned.crt /etc/pki/ca-trust/source/anchors/selfsigned.crt

USER root
RUN update-ca-trust extract
RUN keytool -importcert -alias minio-ca \
    -file /etc/pki/ca-trust/source/anchors/selfsigned.crt \
    -keystore $JAVA_HOME/lib/security/cacerts \
    -storepass changeit -noprompt

USER trino