# Makefile for Hive metastore deployment

NAMESPACE ?= hive
POSTGRES_OPERATOR ?= bitnami/postgresql

# Optional targets for specific components
.PHONY: build-metastore-custom-dockerfile build-schematool-custom-dockerfile install uninstall release-docker-images

build-metastore-custom-dockerfile:
	@set -ex; \
	docker build --progress=plain \
		-t huusy/hive-metastore-custom:3.0.0 \
		-f infra/services/hive/metastore/Dockerfile .

build-schematool-custom-dockerfile:
	@set -ex; \
	docker build --progress=plain \
		-t huusy/hive-schematool-custom:4.0.0 \
		-f infra/services/hive/schematool/Dockerfile .

install:
	@set -ex; \
	kubectl delete secret hive-metastore-secret --namespace $(NAMESPACE) || true; \
	kubectl create secret generic hive-metastore-secret \
		--from-literal=POSTGRES_URL=jdbc:postgresql://hive-metastore-postgres-postgresql.hive.svc.cluster.local:5432/postgres \
		--from-literal=POSTGRES_USERNAME=postgres \
		--from-literal=POSTGRES_PASSWORD=postgres \
		--from-literal=S3_WAREHOUSE_DIR=s3a://hive-warehouse \
		--namespace $(NAMESPACE); \
	helm upgrade --install --namespace $(NAMESPACE) \
		hive-metastore-postgres $(POSTGRES_OPERATOR) \
		--set global.postgresql.auth.postgresPassword=postgres \
		--set global.postgresql.auth.database=postgres; \
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
