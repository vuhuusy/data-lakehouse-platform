.DEFAULT_GOAL := help

NAMESPACE ?= airflow
CHART_POSTGRESQL ?= bitnami/postgresql
CHART_REDIS ?= bitnami/redis
AIRFLOW_OPERATOR ?= apache-airflow/airflow

.PHONY: \
	build-custom-dockerfile \
	release-docker-images \
	install install-all install-postgresql-redis \
	install-airflow \
	uninstall uninstall-all \
	uninstall-postgresql-redis \
	uninstall-airflow \
	create-namespace \
	create-web-nodeport \
	delete-web-nodeport \
	create-clusterrolebinding-for-spark-applications \
	help

install: create-namespace install-postgresql-redis install-airflow create-web-nodeport

uninstall: uninstall-airflow uninstall-postgresql-redis

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

build-custom-dockerfile:
	@set -e; \
	printf '\033[1;33mBuilding custom Airflow Docker image...\033[0m\n'; \
	docker build --progress=plain \
		-t huusy/airflow:2.10.5 \
		-f infra/services/airflow/Dockerfile .; \
	printf '\033[1;32mDocker image built.\033[0m\n'

release-docker-images:
	@set -e; \
	printf '\033[1;33mReleasing Airflow Docker image...\033[0m\n'; \
	docker push huusy/airflow:2.10.5; \
	printf '\033[1;32mDocker image pushed to registry.\033[0m\n'

install-postgresql-redis:
	@set -e; \
	printf '\033[1;33mInstalling PostgreSQL and Redis...\033[0m\n'; \
	helm repo list | grep -q bitnami || helm repo add bitnami https://charts.bitnami.com/bitnami; \
	helm repo update; \
	helm upgrade --install postgresql $(CHART_POSTGRESQL) \
		--namespace $(NAMESPACE) \
		--create-namespace \
		-f infra/services/airflow/postgresql/values.yaml; \
	helm upgrade --install redis $(CHART_REDIS) \
		--namespace $(NAMESPACE) \
		-f infra/services/airflow/redis/values.yaml; \
	printf '\033[1;32mPostgreSQL and Redis installed.\033[0m\n'

uninstall-postgresql-redis:
	@set -e; \
	printf '\033[1;33mUninstalling PostgreSQL and Redis...\033[0m\n'; \
	helm uninstall postgresql --namespace $(NAMESPACE) || true; \
	helm uninstall redis --namespace $(NAMESPACE) || true; \
	printf '\033[1;32mPostgreSQL and Redis uninstalled.\033[0m\n'

install-airflow:
	@set -e; \
	printf '\033[1;33mInstalling Airflow...\033[0m\n'; \
	helm repo list | grep -q apache-airflow || helm repo add apache-airflow https://airflow.apache.org; \
	helm repo update; \
	helm upgrade --install airflow $(AIRFLOW_OPERATOR) \
		--namespace $(NAMESPACE) \
		-f infra/services/airflow/operator/values.yaml; \
	printf '\033[1;32mAirflow installed.\033[0m\n'

uninstall-airflow:
	@set -e; \
	printf '\033[1;33mUninstalling Airflow...\033[0m\n'; \
	helm uninstall airflow --namespace $(NAMESPACE) || true; \
	printf '\033[1;32mAirflow uninstalled.\033[0m\n'

create-clusterrolebinding-for-spark-applications:
	@set -e; \
	printf '\033[1;33mCreating clusterrolebinding for Spark applications...\033[0m\n'; \
	kubectl create clusterrolebinding default-admin \
		--clusterrole cluster-admin \
		--serviceaccount=$(NAMESPACE):airflow-worker \
		--namespace $(NAMESPACE); \
	printf '\033[1;32mClusterrolebinding created.\033[0m\n'

create-web-nodeport:
	@set -e; \
	printf '\033[1;33mCreating NodePort service for Airflow Web UI...\033[0m\n'; \
	kubectl apply -f infra/services/airflow/web-nodeport.yaml; \
	printf '\033[1;32mNodePort service created.\033[0m\n'

delete-web-nodeport:
	@set -e; \
	printf '\033[1;33mDeleting NodePort service for Airflow Web UI...\033[0m\n'; \
	kubectl delete -f infra/services/airflow/web-nodeport.yaml || true; \
	printf '\033[1;32mNodePort service deleted.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install                                   - Install Airflow with PostgreSQL, Redis, Web UI"
	@echo "  make uninstall                                 - Uninstall all Airflow components"
	@echo "  make create-namespace                          - Create Kubernetes namespace for Airflow"
	@echo "  make build-custom-dockerfile                   - Build custom Airflow Docker image"
	@echo "  make release-docker-images                     - Push Airflow image to registry"
	@echo "  make install-postgresql-redis                  - Install PostgreSQL and Redis"
	@echo "  make uninstall-postgresql-redis                - Uninstall PostgreSQL and Redis"
	@echo "  make install-airflow                           - Install Airflow using Helm"
	@echo "  make uninstall-airflow                         - Uninstall Airflow"
	@echo "  make create-web-nodeport                       - Create NodePort service for Airflow Web UI"
	@echo "  make delete-web-nodeport                       - Delete NodePort service for Airflow Web UI"
	@echo "  make create-clusterrolebinding-for-spark-applications - Create ClusterRoleBinding for Spark apps"
