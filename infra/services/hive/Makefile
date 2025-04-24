.DEFAULT_GOAL := help

# Makefile for Hive metastore deployment

NAMESPACE ?= hive
POSTGRES_CHART ?= bitnami/postgresql

# Optional targets for specific components
.PHONY: \
	build-metastore-custom-dockerfile \
	build-schematool-custom-dockerfile \
	create-minio-secret \
	install \
	uninstall \
	release-docker-images \
	create-namespace \
	help

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

build-metastore-custom-dockerfile:
	@set -e; \
	docker build \
		-t huusy/hive-metastore-custom:3.0.0 \
		-f infra/services/hive/metastore/Dockerfile .

build-schematool-custom-dockerfile:
	@set -e; \
	docker build \
		-t huusy/hive-schematool-custom:4.0.0 \
		-f infra/services/hive/schematool/Dockerfile .

create-minio-secret:
	@set -e; \
	kubectl delete secret minio-secret --namespace $(NAMESPACE) || true; \
	kubectl create secret generic minio-secret \
		--from-literal=ENDPOINT=minio.minio.svc.cluster.local:9000 \
		--from-literal=AWS_ACCESS_KEY_ID=minio \
		--from-literal=AWS_SECRET_ACCESS_KEY=minio123 \
		--namespace $(NAMESPACE); \

install:
	@set -e; \
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -; \

	kubectl delete secret hive-metastore-secret --namespace $(NAMESPACE) || true; \
	kubectl create secret generic hive-metastore-secret \
		--from-literal=POSTGRES_URL=jdbc:postgresql://hive-metastore-postgres-postgresql.hive.svc.cluster.local:5432/metastore \
		--from-literal=POSTGRES_USERNAME=hive \
		--from-literal=POSTGRES_PASSWORD=hive \
		--from-literal=S3_WAREHOUSE_DIR=s3a://hive-warehouse \
		--namespace $(NAMESPACE); \
	helm upgrade --install -f infra/services/hive/database/values.yaml --namespace $(NAMESPACE) \
		hive-metastore-postgres $(POSTGRES_CHART); \
	kubectl apply -f infra/services/hive/schematool/job.yaml --namespace $(NAMESPACE); \
	kubectl apply -f infra/services/hive/metastore/deployment.yaml --namespace $(NAMESPACE); \
	kubectl apply -f infra/services/hive/metastore/service.yaml --namespace $(NAMESPACE)

uninstall:
	@set -ex; \
	kubectl delete -f infra/services/hive/metastore/service.yaml --namespace $(NAMESPACE); \
	kubectl delete -f infra/services/hive/metastore/deployment.yaml --namespace $(NAMESPACE); \
	kubectl delete -f infra/services/hive/schematool/job.yaml --namespace $(NAMESPACE); \
	helm uninstall --namespace $(NAMESPACE) \
		hive-metastore-postgres

release-docker-images:
	@set -ex; \
	docker push huusy/hive-metastore-custom:3.0.0; \
	docker push huusy/hive-schematool-custom:4.0.0

help:
	@echo "Makefile for Hive metastore deployment"
	@echo "Usage:"
	@echo "  make install                - Install Hive metastore and dependencies"
	@echo "  make uninstall              - Uninstall Hive metastore and dependencies"
	@echo "  make build-metastore-custom-dockerfile - Build custom Docker image for Hive metastore"
	@echo "  make build-schematool-custom-dockerfile - Build custom Docker image for Hive schematool"
	@echo "  make release-docker-images  - Push custom Docker images to registry"