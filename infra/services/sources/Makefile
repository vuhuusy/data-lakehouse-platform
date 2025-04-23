# Makefile for source systems

NAMESPACE ?= financial-ops
POSTGRES_CHART ?= bitnami/postgresql

# Optional targets for specific components
.PHONY: \
	install-postgres \
	uninstall-postgres

create-init-sql-configmap:
	@set -e; \
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -; \
	kubectl delete configmap postgres-init-sql --namespace $(NAMESPACE) || true; \
	kubectl create configmap postgres-init-sql \
		--from-file=postgresql.conf=infra/services/sources/init.sql \
		--namespace $(NAMESPACE)

install-postgres:
	@set -e; \
	kubectl delete configmap postgresql-conf --namespace $(NAMESPACE) || true; \
	kubectl create configmap postgresql-conf \
		--from-file=postgresql.conf=infra/services/sources/postgresql.conf \
		--namespace $(NAMESPACE); \
	helm upgrade --install --namespace $(NAMESPACE) \
		postgres-financial-ops $(POSTGRES_CHART)

uninstall-postgres:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		postgres-financial-ops