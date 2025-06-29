.DEFAULT_GOAL := help

NAMESPACE ?= datahub
DATAHUB_CHART ?= datahub/datahub
DATAHUB_PREREQ_CHART ?= datahub/datahub-prerequisites
MYSQL_SECRET_NAME ?= mysql-secrets
NEO4J_SECRET_NAME ?= neo4j-secrets

.PHONY: \
	install uninstall \
	create-namespace \
	create-secrets \
	install-prerequisites \
	install-datahub \
	create-web-nodeport \
	help

install: create-namespace create-secrets install-prerequisites install-datahub create-web-nodeport

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

create-secrets:
	@set -e; \
	printf '\033[1;33mCreating MySQL & Neo4j secrets...\033[0m\n'; \
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -; \
	kubectl delete secret $(MYSQL_SECRET_NAME) -n $(NAMESPACE) --ignore-not-found; \
	kubectl delete secret $(NEO4J_SECRET_NAME) -n $(NAMESPACE) --ignore-not-found; \
	kubectl create secret generic $(MYSQL_SECRET_NAME) --from-literal=mysql-root-password=datahub -n $(NAMESPACE); \
	kubectl create secret generic $(NEO4J_SECRET_NAME) --from-literal=neo4j-password=datahub -n $(NAMESPACE); \
	printf '\033[1;32mSecrets created.\033[0m\n'

install-prerequisites:
	@set -e; \
	printf '\033[1;33mInstalling DataHub prerequisites...\033[0m\n'; \
	helm repo list | grep -q datahub || helm repo add datahub https://helm.datahubproject.io/; \
	helm repo update; \
	helm upgrade --install prerequisites $(DATAHUB_PREREQ_CHART) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		-f infra/services/datahub/prerequisites/values.yaml; \
	printf '\033[1;32mPrerequisites installed.\033[0m\n'

install-datahub:
	@set -e; \
	printf '\033[1;33mInstalling DataHub...\033[0m\n'; \
	helm upgrade --install datahub $(DATAHUB_CHART) \
		--namespace $(NAMESPACE) \
		-f infra/services/datahub/values.yaml; \
	printf '\033[1;32mDataHub installed.\033[0m\n'

create-web-nodeport:
	@set -e; \
	printf '\033[1;33mCreating NodePort for DataHub Web UI...\033[0m\n'; \
	kubectl apply -f infra/services/datahub/web-nodeport.yaml -n $(NAMESPACE); \
	printf '\033[1;32mNodePort created.\033[0m\n'

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling DataHub...\033[0m\n'; \
	helm uninstall datahub -n $(NAMESPACE) || true; \
	helm uninstall prerequisites -n $(NAMESPACE) || true; \
	kubectl delete secret $(MYSQL_SECRET_NAME) -n $(NAMESPACE) || true; \
	kubectl delete secret $(NEO4J_SECRET_NAME) -n $(NAMESPACE) || true; \
	kubectl delete service datahub-web-nodeport -n $(NAMESPACE) || true; \
	printf '\033[1;32mUninstallation complete.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install               - Install DataHub (prerequisites + app + NodePort)"
	@echo "  make uninstall             - Uninstall DataHub and cleanup secrets/services"
	@echo "  make create-namespace      - Create namespace '$(NAMESPACE)'"
	@echo "  make create-secrets        - Create MySQL/Neo4j secrets in '$(NAMESPACE)'"
	@echo "  make install-prerequisites - Install DataHub prerequisite components"
	@echo "  make install-datahub       - Install main DataHub chart"
	@echo "  make create-web-nodeport   - Create NodePort service for DataHub web UI"
	@echo "  make help                  - Show this help message"
