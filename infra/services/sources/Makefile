.DEFAULT_GOAL := help

NAMESPACE ?= financial-ops
POSTGRES_CHART ?= bitnami/postgresql

.PHONY: \
	install uninstall \
	install-postgres \
	uninstall-postgres \
	create-namespace \
	create-init-sql-configmap \
	expose-postgres-nodeport \
	help

install: create-namespace create-init-sql-configmap install-postgres expose-postgres-nodeport

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

create-init-sql-configmap:
	@set -e; \
	printf '\033[1;33mCreating init.sql ConfigMap...\033[0m\n'; \
	kubectl delete configmap postgres-init-sql --namespace $(NAMESPACE) || true; \
	kubectl create configmap postgres-init-sql \
		--from-file=init.sql=infra/services/sources/init.sql \
		--namespace $(NAMESPACE); \
	printf '\033[1;32mInit ConfigMap created.\033[0m\n'

install-postgres:
	@set -e; \
	printf '\033[1;33mInstalling PostgreSQL...\033[0m\n'; \
	kubectl delete configmap postgresql-conf --namespace $(NAMESPACE) || true; \
	kubectl create configmap postgresql-conf \
		--from-file=postgresql.conf=infra/services/sources/postgresql.conf \
		--namespace $(NAMESPACE); \
	helm repo list | grep -q bitnami || helm repo add bitnami https://charts.bitnami.com/bitnami; \
	helm repo update; \
	helm upgrade --install postgres-financial-ops $(POSTGRES_CHART) \
		--namespace $(NAMESPACE) \
		-f infra/services/sources/values.yaml; \
	printf '\033[1;32mPostgreSQL installed.\033[0m\n'

expose-postgres-nodeport:
	@set -e; \
	printf '\033[1;33mExposing PostgreSQL via NodePort...\033[0m\n'; \
	kubectl apply -f infra/services/sources/postgres-nodeport.yaml; \
	printf '\033[1;32mNodePort service created.\033[0m\n'

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling PostgreSQL and namespace...\033[0m\n'; \
	helm uninstall postgres-financial-ops --namespace $(NAMESPACE) || true; \
	kubectl delete namespace $(NAMESPACE) || true; \
	printf '\033[1;32mUninstallation complete.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install                      - Install PostgreSQL with init.sql configmap and NodePort"
	@echo "  make uninstall                    - Uninstall PostgreSQL and delete namespace"
	@echo "  make create-namespace             - Create Kubernetes namespace '$(NAMESPACE)'"
	@echo "  make create-init-sql-configmap    - Create init.sql ConfigMap"
	@echo "  make install-postgres             - Install PostgreSQL with custom config"
	@echo "  make expose-postgres-nodeport     - Expose PostgreSQL via NodePort service"
