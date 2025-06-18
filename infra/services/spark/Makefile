.DEFAULT_GOAL := help

NAMESPACE ?= spark-operator
SPARK_OPERATOR ?= spark-operator/spark-operator

.PHONY: install uninstall \
	create-namespace \
	install-spark \
	uninstall-spark \
	build-spark-application-dockerfile \
	release-docker-image

install: create-namespace create-minio-secret install-spark

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-spark:
	@set -e; \
	helm upgrade --install --namespace $(NAMESPACE) \
		--values infra/services/spark/operator/values.yaml \
    	spark-operator $(SPARK_OPERATOR)

uninstall-spark:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		spark-operator

create-minio-secret:
	@kubectl delete secret minio-secret --namespace $(NAMESPACE) || true; \
	kubectl create secret generic minio-secret \
		--from-literal=AWS_ACCESS_KEY_ID=minio \
		--from-literal=AWS_SECRET_ACCESS_KEY=minio123 \
		--from-literal=ENDPOINT=https://minio.minio.svc.cluster.local:443 \
		--from-literal=AWS_REGION=us-east-1 \
		--namespace $(NAMESPACE)

build-spark-application-dockerfile:
	@set -e; \
	docker build \
		-t huusy/spark-application:3.5.3 \
		-f infra/services/spark/Dockerfile .

release-docker-image:
	@set -e; \
	docker push huusy/spark-application:3.5.3
