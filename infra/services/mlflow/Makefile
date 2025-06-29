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

server:
	@set -e; \
	printf '\033[1;33mRunning local MLflow model server...\033[0m\n'; \
	docker run -p 5001:8080 \
		-e MLFLOW_TRACKING_URI=http://103.82.133.158:30500 \
		-e MLFLOW_S3_ENDPOINT_URL=https://103.82.133.158:30900 \
		-e AWS_ACCESS_KEY_ID=minio \
		-e AWS_SECRET_ACCESS_KEY=minio123 \
		-e MLFLOW_S3_IGNORE_TLS=true \
		-v ~/.mlflow:/root/.mlflow \
		$(IMAGE_TAG) \
		mlflow models serve -m "runs:/ac6b711d418f48d4abef42374c9b50c2/model" --no-conda --host 0.0.0.0 --port 8080

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
