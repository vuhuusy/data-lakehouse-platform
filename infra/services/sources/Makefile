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
		--namespace $(NAMESPACE); \
	helm upgrade --install --namespace $(NAMESPACE) \
		postgres-financial-ops $(POSTGRES_CHART) \
		-f infra/services/sources/values.yaml

copy-csv-to-pod:
	@set -e; \
	PG_POD=$$(kubectl get pod -n $(NAMESPACE) -l app.kubernetes.io/component=primary -o jsonpath='{.items[0].metadata.name}'); \
	kubectl cp infra/services/sources/data-source/user.csv $(NAMESPACE)/$$PG_POD:/tmp/user.csv; \
	kubectl cp infra/services/sources/data-source/card.csv $(NAMESPACE)/$$PG_POD:/tmp/card.csv; \
	kubectl cp infra/services/sources/data-source/mcc.csv $(NAMESPACE)/$$PG_POD:/tmp/mcc.csv; \
	kubectl cp infra/services/sources/data-source/merchant.csv $(NAMESPACE)/$$PG_POD:/tmp/merchant.csv

insert-csv:
	@set -e; \
	PG_POD=$$(kubectl get pod -n $(NAMESPACE) -l app.kubernetes.io/component=primary -o jsonpath='{.items[0].metadata.name}'); \
	kubectl exec -n $(NAMESPACE) -i $$PG_POD -- bash -c "export PGPASSWORD=postgres; psql -U postgres -d financial_ops" <<'EOF'
	\COPY core.user_account FROM '/tmp/user.csv' WITH (FORMAT csv, HEADER true);
	\COPY core.card FROM '/tmp/card.csv' WITH (FORMAT csv, HEADER true);
	\COPY core.mcc FROM '/tmp/mcc.csv' WITH (FORMAT csv, HEADER true);
	\COPY core.merchant FROM '/tmp/merchant.csv' WITH (FORMAT csv, HEADER true);
	EOF

uninstall-postgres:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		postgres-financial-ops || true;\
	kubectl delete namespace $(NAMESPACE)