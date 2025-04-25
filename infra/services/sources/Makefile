# Makefile for source systems

NAMESPACE ?= financial-ops
POSTGRES_CHART ?= bitnami/postgresql

# Optional targets for specific components
.PHONY: \
	install-postgres \
	uninstall-postgres \
	create-namespace \
	create-init-sql-configmap \
	create-minio-loader-job

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

create-init-sql-configmap:
	@set -e; \
	kubectl delete configmap postgres-init-sql --namespace $(NAMESPACE) || true; \
	kubectl create configmap postgres-init-sql \
		--from-file=init.sql=infra/services/sources/init.sql \
		--namespace $(NAMESPACE)

install-postgres:
	@set -e; \
	kubectl delete configmap postgresql-conf --namespace $(NAMESPACE) || true; \
	kubectl create configmap postgresql-conf \
		--from-file=postgresql.conf=infra/services/sources/postgresql.conf \
		--namespace $(NAMESPACE); \
	helm upgrade --install --namespace $(NAMESPACE) \
		postgres-financial-ops $(POSTGRES_CHART) \
		-f infra/services/sources/values.yaml

expose-postgres-nodeport:
	@kubectl apply -f infra/services/sources/postgres-nodeport.yaml

uninstall-postgres:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		postgres-financial-ops || true;\
	kubectl delete namespace $(NAMESPACE)