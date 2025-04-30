# Makefile for DataHub deployment

NAMESPACE ?= datahub
MYSQL_SECRET_NAME ?= mysql-secrets
NEO4J_SECRET_NAME ?= neo4j-secrets
DATAHUB_CHART ?= datahub/datahub
DATAHUB_PREREQ_CHART ?= datahub/datahub-prerequisites

.PHONY: \
	create-secrets \
	install \
	uninstall \
	release-docker-images \
	create-web-nodeport

create-secrets:
	@set -e; \
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -; \
	kubectl delete secret $(MYSQL_SECRET_NAME) -n $(NAMESPACE) --ignore-not-found; \
	kubectl delete secret $(NEO4J_SECRET_NAME) -n $(NAMESPACE) --ignore-not-found; \
	kubectl create secret generic $(MYSQL_SECRET_NAME) --from-literal=mysql-root-password=datahub -n $(NAMESPACE); \
	kubectl create secret generic $(NEO4J_SECRET_NAME) --from-literal=neo4j-password=datahub -n $(NAMESPACE)

install:
	@set -e; \
	helm upgrade --install prerequisites $(DATAHUB_PREREQ_CHART) -n $(NAMESPACE) --create-namespace -f infra/services/datahub/prerequisites/values.yaml ; \
	helm upgrade --install datahub $(DATAHUB_CHART) -n $(NAMESPACE) -f infra/services/datahub/values.yaml

create-web-nodeport:
	@set -e; \
	kubectl apply -f infra/services/datahub/web-nodeport.yaml -n datahub

uninstall:
	@set -e; \
	helm uninstall datahub -n $(NAMESPACE) || true; \
	helm uninstall datahub-prerequisites -n $(NAMESPACE) || true; \
	kubectl delete secret $(MYSQL_SECRET_NAME) -n $(NAMESPACE) || true; \
	kubectl delete secret $(NEO4J_SECRET_NAME) -n $(NAMESPACE) || true; \
	kubectl delete service datahub-web-nodeport -n $(NAMESPACE) || true
