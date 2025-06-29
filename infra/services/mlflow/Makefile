.DEFAULT_GOAL := help

NAMESPACE ?= mlflow
CHART ?= community-charts/mlflow
IMAGE_TAG ?= huusy/mlflow:v2.12.1

.PHONY: \
	install uninstall \
	create-namespace \
	install-mlflow \
	expose-mlflow-service \
	create-minio-ca-configmap \
	build-image release-image \
	server help

install: create-namespace create-minio-ca-configmap install-mlflow expose-mlflow-service

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-mlflow:
	@set -e; \
	printf '\033[1;33mInstalling MLflow...\033[0m\n'; \
	helm repo list | grep -q community-charts || \
		helm repo add community-charts https://community-charts.github.io/helm-charts; \
	helm repo update; \
	helm upgrade --install mlflow $(CHART) \
		--namespace $(NAMESPACE) \
		-f infra/services/mlflow/values.yaml; \
	printf '\033[1;32mMLflow installed.\033[0m\n'

expose-mlflow-service:
	@set -e; \
	printf '\033[1;33mExposing MLflow via NodePort...\033[0m\n'; \
	kubectl apply -n $(NAMESPACE) -f infra/services/mlflow/mlflow-nodeport.yaml; \
	printf '\033[1;32mMLflow NodePort exposed.\033[0m\n'

create-minio-ca-configmap:
	@set -e; \
	printf '\033[1;33mCreating MinIO CA ConfigMap...\033[0m\n'; \
	kubectl delete configmap minio-ca-configmap -n $(NAMESPACE) || true; \
	kubectl create configmap minio-ca-configmap \
		--from-file=ca.crt=infra/certs/minio/selfsigned.crt \
		-n $(NAMESPACE); \
	printf '\033[1;32mMinIO CA ConfigMap created.\033[0m\n'

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling MLflow...\033[0m\n'; \
	helm uninstall mlflow --namespace $(NAMESPACE) || true; \
	kubectl delete configmap minio-ca-configmap --namespace $(NAMESPACE) || true; \
	kubectl delete service mlflow --namespace $(NAMESPACE) || true; \
	printf '\033[1;32mMLflow uninstalled.\033[0m\n'

build-image:
	@set -e; \
	printf '\033[1;33mBuilding MLflow Docker image...\033[0m\n'; \
	docker build -t $(IMAGE_TAG) infra/services/mlflow/.; \
	printf '\033[1;32mImage built: $(IMAGE_TAG)\033[0m\n'

release-image:
	@set -e; \
	printf '\033[1;33mPushing MLflow Docker image...\033[0m\n'; \
	docker push $(IMAGE_TAG); \
	printf '\033[1;32mImage pushed.\033[0m\n'

mlflow-serve:
	@set -e; \
	printf '\033[1;33mRunning local MLflow model server...\033[0m\n'; \
	kubectl apply -f infra/services/mlflow/mlflow-serve.yaml; \
	kubectl wait --for=condition=available --timeout=90s deployment/mlflow-model-serving -n $(NAMESPACE); \
	printf '\033[1;32mMLflow model server is running.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install                    - Install MLflow with NodePort and MinIO CA config"
	@echo "  make uninstall                  - Uninstall MLflow and cleanup"
	@echo "  make build-image                - Build MLflow Docker image ($(IMAGE_TAG))"
	@echo "  make release-image              - Push image to registry"
	@echo "  make server                     - Run local MLflow model server"
	@echo "  make create-namespace           - Create MLflow namespace ($(NAMESPACE))"
	@echo "  make create-minio-ca-configmap  - Create ConfigMap with MinIO CA cert"
	@echo "  make expose-mlflow-service      - Expose MLflow Web UI via NodePort"
