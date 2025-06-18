.DEFAULT_GOAL := help

NAMESPACE ?= airflow
CHART_POSTGRESQL ?= bitnami/postgresql
CHART_REDIS ?= bitnami/redis
AIRFLOW_OPERATOR ?= apache-airflow/airflow

.PHONY: \
	build-custom-dockerfile \
	release-docker-images \
	install-all install-postgresql-redis \
	install-airflow \
	uninstall-all \
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
	docker build --progress=plain \
		-t huusy/airflow:2.10.5 \
		-f infra/services/airflow/Dockerfile .

release-docker-images:
	@set -e; \
	docker push huusy/airflow:2.10.5

install-postgresql-redis:
	@set -e; \
	@echo "Installing PostgreSQL and Redis for Airflow..."; \
	helm repo list | grep -q bitnami || helm repo add bitnami https://charts.bitnami.com/bitnami
	helm repo update

	helm upgrade --install postgresql $(CHART_POSTGRESQL) \
	  --namespace $(NAMESPACE) \
	  --create-namespace \
	  -f infra/services/airflow/postgresql/values.yaml; \
	helm upgrade --install redis $(CHART_REDIS) \
	  --namespace $(NAMESPACE) \
	  -f infra/services/airflow/redis/values.yaml
	@echo "PostgreSQL and Redis installation complete."

uninstall-postgresql-redis:
	@set -e; \
	@echo "Uninstalling PostgreSQL and Redis..."; \
	helm uninstall postgresql --namespace $(NAMESPACE) || true; \
	helm uninstall redis --namespace $(NAMESPACE) || true
	@echo "PostgreSQL and Redis uninstallation complete."

install-airflow:
	@set -e; \
	@echo "Installing Airflow..."; \
	helm repo list | grep -q apache-airflow || helm repo add apache-airflow https://airflow.apache.org
	helm repo update

	helm upgrade --install airflow $(AIRFLOW_OPERATOR) \
	  --namespace $(NAMESPACE) \
	  -f infra/services/airflow/operator/values.yaml
	@echo "Airflow installation complete."

# Uninstall Airflow
uninstall-airflow:
	@set -e; \
	@echo "Uninstalling Airflow..."; \
	helm uninstall airflow --namespace $(NAMESPACE) || true
	@echo "Airflow uninstallation complete."

# Create cluster role binding for Spark applications
# This is necessary for Airflow to run Spark jobs in the cluster
create-clusterrolebinding-for-spark-applications:
	@set -e; \
	kubectl create clusterrolebinding default-admin \
		--clusterrole cluster-admin \
		--serviceaccount=$(NAMESPACE):airflow-worker \
		--namespace $(NAMESPACE)
	@echo "Cluster role binding for Spark applications created."

create-web-nodeport:
	@set -e; \
	@echo "Creating NodePort service for Airflow web server..."; \
	kubectl apply -f infra/services/airflow/web-nodeport.yaml
	@echo "NodePort service for Airflow web server created."

delete-web-nodeport:
	@set -e; \
	@echo "Deleting NodePort service for Airflow web server..."; \
	kubectl delete -f infra/services/airflow/web-nodeport.yaml
	@echo "NodePort service for Airflow web server deleted."

help:
	@echo "Makefile commands:"
	@echo "  make install            				- Install all Airflow components (PostgreSQL, Redis, Airflow)"
	@echo "  make uninstall          				- Uninstall all Airflow components"
	@echo "  make create-namespace   				- Create the Airflow namespace"
	@echo "  make build-custom-dockerfile 			- Build custom Airflow Docker image"
	@echo "  make release-docker-images 			- Push custom Airflow Docker image to registry"
	@echo "  make install-postgresql-redis 			- Install PostgreSQL and Redis for Airflow"
	@echo "  make uninstall-postgresql-redis 		- Uninstall PostgreSQL and Redis"
	@echo "  make install-airflow     				- Install Airflow"
	@echo "  make uninstall-airflow   				- Uninstall Airflow"
	@echo "  make create-web-nodeport 				- Create NodePort service for Airflow web server"
	@echo "  make delete-web-nodeport 				- Delete NodePort service for Airflow web server"
	@echo "  make create-clusterrolebinding-for-spark-applications - Create cluster role binding for Spark applications"
	@echo "  make help                				- Show this help message"