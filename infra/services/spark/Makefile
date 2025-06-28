.DEFAULT_GOAL := help

NAMESPACE ?= spark-operator
SPARK_OPERATOR ?= spark-operator/spark-operator

.PHONY: \
	install uninstall \
	create-namespace \
	install-spark \
	uninstall-spark \
	create-minio-secret \
	build-spark-application-dockerfile \
	release-docker-image \
	help

install: create-namespace create-minio-secret install-spark

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-spark:
	@set -e; \
	printf '\033[1;33mInstalling Spark Operator...\033[0m\n'; \
	helm repo list | grep -q spark-operator || helm repo add spark-operator https://kubeflow.github.io/spark-operator; \
	helm upgrade --install spark-operator $(SPARK_OPERATOR) \
		--namespace $(NAMESPACE) \
		--values infra/services/spark/operator/values.yaml; \
	printf '\033[1;32mSpark Operator installed.\033[0m\n'

uninstall-spark:
	@set -e; \
	printf '\033[1;33mUninstalling Spark Operator...\033[0m\n'; \
	helm uninstall spark-operator --namespace $(NAMESPACE); \
	printf '\033[1;32mSpark Operator uninstalled.\033[0m\n'

create-minio-secret:
	@set -e; \
	printf '\033[1;33mCreating MinIO secret...\033[0m\n'; \
	kubectl delete secret minio-secret --namespace $(NAMESPACE) || true; \
	kubectl create secret generic minio-secret \
		--from-literal=AWS_ACCESS_KEY_ID=minio \
		--from-literal=AWS_SECRET_ACCESS_KEY=minio123 \
		--from-literal=ENDPOINT=https://minio.minio.svc.cluster.local:443 \
		--from-literal=AWS_REGION=us-east-1 \
		--namespace $(NAMESPACE); \
	printf '\033[1;32mMinIO secret created.\033[0m\n'

build-spark-application-dockerfile:
	@set -e; \
	printf '\033[1;33mBuilding Spark Application Docker image...\033[0m\n'; \
	docker build \
		-t huusy/spark-application:3.5.3 \
		-f infra/services/spark/Dockerfile .; \
	printf '\033[1;32mDocker image built.\033[0m\n'

release-docker-image:
	@set -e; \
	printf '\033[1;33mReleasing Spark Application Docker image...\033[0m\n'; \
	docker push huusy/spark-application:3.5.3; \
	printf '\033[1;32mDocker image pushed to registry.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install                         - Install Spark Operator and MinIO secret"
	@echo "  make uninstall                       - Uninstall Spark Operator"
	@echo "  make create-namespace                - Create namespace if not exists"
	@echo "  make install-spark                   - Install Spark Operator only"
	@echo "  make uninstall-spark                 - Uninstall Spark Operator only"
	@echo "  make create-minio-secret             - Create MinIO credentials secret in namespace"
	@echo "  make build-spark-application-dockerfile - Build Spark application Docker image"
	@echo "  make release-docker-image            - Push Spark application image to Docker registry"
