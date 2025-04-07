# Makefile for project
.DEFAULT_GOAL := help
NAMESPACE ?= lakehouse

# Define phony targets
.PHONY: init install uninstall expose-ports help

init:
	@set -ex; \
	(kubectl create namespace lakehouse || true) & kubectl config set-context --current --namespace=lakehouse; \
	make -f infra/services/minio/Makefile generate-self-signed-cert; \
	make -f infra/services/minio/Makefile register-self-signed-cert; \
	make -f infra/services/nifi/Makefile setup-cert-manager; \
	make -f infra/services/trino/Makefile build-trino-custom-dockerfile; \
	make -f infra/services/trino/Makefile release-docker-images; \

# 	make -f scripts/minio/Makefile generate-self-signed-cert; \
# 	make -f scripts/minio/Makefile register-self-signed-cert; \
# 	make -f scripts/spark/Makefile build-spark-application-dockerfile; \
# 	make -f scripts/spark/Makefile build-spark-write-minio-dockerfile; \
# 	make -f scripts/spark/Makefile release-docker-images; \
# 	make -f scripts/airflow/Makefile build-custom-dockerfile; \
# 	make -f scripts/airflow/Makefile release-docker-images; \
# 	make -f scripts/hive/Makefile build-metastore-custom-dockerfile; \
# 	make -f scripts/hive/Makefile build-schematool-custom-dockerfile; \
# 	make -f scripts/hive/Makefile release-docker-images; \
# 	make -f scripts/spark/Makefile build-spark-create-hive-table-dockerfile; \
# 	make -f scripts/kafka/Makefile generate-self-signed-cert-keystore-truststore; \
# 	make -f scripts/kafka/Makefile register-self-signed-cert-keystore-truststore; \
# 	make -f scripts/trino/Makefile build-trino-custom-dockerfile; \
# 	make -f scripts/trino/Makefile release-docker-images

install:
	@set -ex; \
	make -f infra/services/minio/Makefile install-minio; \
	make -f infra/services/nifi/Makefile install-nifi; \
	make -f infra/services/nessie/Makefile install-nessie; \
	make -f infra/services/trino/Makefile install-trino; \

# 	make -f scripts/spark/Makefile install; \
# 	make -f scripts/airflow/Makefile install; \
# 	make -f scripts/hive/Makefile install; \
# 	make -f scripts/kafka/Makefile install; \
# 	make -f scripts/sources/Makefile install-postgres; \
# 	make -f scripts/kafka-connect/Makefile install; \
# 	make -f scripts/trino/Makefile install

uninstall:
	@set -ex; \
	make -f infra/services/minio/Makefile uninstall-minio || true; \
	make -f infra/services/nifi/Makefile uninstall-nifi || true; \
	make -f infra/services/nessie/Makefile uninstall-nessie || true; \
	make -f infra/services/trino/Makefile uninstall-trino || true; \

# 	make -f scripts/spark/Makefile uninstall || true; \
# 	make -f scripts/airflow/Makefile uninstall || true; \
# 	make -f scripts/hive/Makefile uninstall || true; \
# 	make -f scripts/kafka/Makefile uninstall || true; \
# 	make -f scripts/sources/Makefile uninstall-postgres || true; \
# 	make -f scripts/kafka-connect/Makefile uninstall || true; \
# 	make -f scripts/trino/Makefile uninstall || true
	kubectl delete namespace lakehouse

expose-ports:
	@set -ex;
	lsof -t -i tcp:9000 | xargs -r kill; \
	lsof -t -i tcp:9443 | xargs -r kill; \
	lsof -t -i tcp:8443 | xargs -r kill; \
	lsof -t -i tcp:19120 | xargs -r kill; \
	lsof -t -i tcp:8080 | xargs -r kill; \
	

# lsof -t -i tcp:8080 | xargs kill; \
# lsof -t -i tcp:5432 | xargs kill; \
# lsof -t -i tcp:8083 | xargs kill; \
# lsof -t -i tcp:8089 | xargs kill; \


	kubectl port-forward service/myminio-hl 		9000 -n lakehouse & \
	kubectl port-forward service/myminio-console 	9443 -n lakehouse & \
	kubectl port-forward service/nifi 				8443 -n lakehouse & \
	kubectl port-forward service/nessie 			19120 -n lakehouse & \
	kubectl port-forward service/trino 				8080 -n lakehouse &
	
# kubectl port-forward service/airflow-operator-webserver 8080 -n lakehouse &
# kubectl port-forward service/postgres-source-postgresql 5432 -n lakehouse &
# kubectl port-forward service/kafka-connect-operator-cp-kafka-connect 8083 -n lakehouse &
# kubectl port-forward service/trino-operator-trino 8089:8080 -n lakehouse &

# # Show help message
help:
	@echo "Makefile commands:"
	@echo "  make init                - Initialize all project dependencies"
	@echo "  make install             - Install all services"
	@echo "  make uninstall           - Uninstall all services"
	@echo "  make expose-ports        - Expose ports for services"