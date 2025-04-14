.DEFAULT_GOAL := help

# Variables
NAMESPACE ?= airflow
CHART_POSTGRESQL ?= bitnami/postgresql
CHART_REDIS ?= bitnami/redis
AIRFLOW_OPERATOR ?= apache-airflow/airflow

# Define phony targets
.PHONY: 
	build-custom-dockerfile \
	release-docker-images \
	install-all install-postgresql-redis \
	install-airflow \
	uninstall-all \
	uninstall-postgresql-redis \
	uninstall-airflow \
	create-clusterrolebinding-for-spark-applications \
	help

# Install all
install-all: install-postgresql-redis install-airflow

# Uninstall all
uninstall-all: uninstall-airflow uninstall-postgresql-redis

# Build custom Dockerfile for Airflow
build-custom-dockerfile:
	@set -e; \
	docker build --progress=plain \
		-t huusy/airflow:2.10.5 \
		-f infra/services/airflow/Dockerfile .

# Release Docker images to Docker Hub
release-docker-images:
	@set -e; \
	docker push huusy/airflow:2.10.5

# Install PostgreSQL and Redis
install-postgresql-redis:
	@set -e; \
	helm upgrade --install postgresql $(CHART_POSTGRESQL) \
	  --namespace $(NAMESPACE) --create-namespace \
	  --values infra/services/airflow/postgresql/values.yaml; \
	helm upgrade --install redis $(CHART_REDIS) \
	  --namespace $(NAMESPACE) \
	  --values infra/services/airflow/redis/values.yaml

# Uninstall PostgreSQL and Redis
uninstall-postgresql-redis:
	@set -e; \
	helm uninstall postgresql --namespace $(NAMESPACE) || true; \
	helm uninstall redis --namespace $(NAMESPACE) || true

# Install Airflow
install-airflow:
	@set -e; \
	helm upgrade --install airflow $(AIRFLOW_OPERATOR) \
	  --namespace $(NAMESPACE) \
	  --values infra/services/airflow/operator/values.yaml

# Uninstall Airflow
uninstall-airflow:
	@set -e; \
	helm uninstall airflow --namespace $(NAMESPACE) || true

# Create cluster role binding for Spark applications
# This is necessary for Airflow to run Spark jobs in the cluster
create-clusterrolebinding-for-spark-applications:
	@set -e; \
	kubectl create clusterrolebinding default-admin \
		--clusterrole cluster-admin \
		--serviceaccount=$(NAMESPACE):airflow-worker \
		--namespace $(NAMESPACE)

help:
	@echo "Makefile commands:"; \
	echo "make install-all                 - Install PostgreSQL, Redis, and Airflow"; \
	echo "make uninstall-all               - Uninstall all components"; \
	echo "make install-postgresql-redis    - Install only PostgreSQL and Redis"; \
	echo "make uninstall-postgresql-redis  - Uninstall only PostgreSQL and Redis"; \
	echo "make install-airflow             - Install only Airflow (assumes external services ready)"; \
	echo "make uninstall-airflow           - Uninstall Airflow"