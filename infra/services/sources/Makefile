# Makefile for source systems

NAMESPACE ?= finance-core
POSTGRES_CHART ?= bitnami/postgresql

# Optional targets for specific components
.PHONY: \
	install-postgres \
	uninstall-postgres

create-configmap:
	@set -e; \
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
		postgres-finance-core $(POSTGRES_CHART) \
		--set global.postgresql.auth.postgresPassword=postgres \
		--set global.postgresql.auth.database=postgres \
		--set primary.existingConfigmap=postgresql-conf

uninstall-postgres:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		postgres-finance-core