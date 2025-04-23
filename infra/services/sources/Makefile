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
		--from-file=init.sql=infra/services/sources/init.sql \
		--namespace $(NAMESPACE)

install-postgres:
	@set -e; \
	kubectl delete configmap postgresql-conf --namespace $(NAMESPACE) || true; \
	kubectl create configmap postgresql-conf \
		--from-file=postgresql.conf=infra/services/sources/postgresql.conf \
	  --from-file=user.csv=infra/services/sources/data-source/user.csv \
		--from-file=card.csv=infra/services/sources/data-source/card.csv \
		--from-file=mcc.csv=infra/services/sources/data-source/mcc.csv \
		--from-file=merchant.csv=infra/services/sources/data-source/merchant.csv \
		--namespace $(NAMESPACE); \
	helm upgrade --install --namespace $(NAMESPACE) \
		postgres-financial-ops $(POSTGRES_CHART) \
		-f infra/services/sources/values.yaml

uninstall-postgres:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		postgres-financial-ops || true;\
	kubectl delete namespace $(NAMESPACE)