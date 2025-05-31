.PHONY: install-mlflow uninstall-mlflow expose-mlflow-service create-minio-ca-configmap

# Install MLflow
install-mlflow:
	@set -e; \
	kubectl get namespace mlflow >/dev/null 2>&1 || kubectl create namespace mlflow; \
	helm upgrade --install mlflow community-charts/mlflow \
		--namespace mlflow \
		-f infra/services/mlflow/values.yaml

# Create MLflow Service with fixed NodePort
expose-mlflow-service:
	@set -e; \
	kubectl apply -f infra/services/mlflow/mlflow-nodeport.yaml -n mlflow

create-minio-ca-configmap:
	@set -e; \
	kubectl create configmap minio-ca-configmap \
	  --from-file=ca.crt=infra/services/minio/selfsigned.crt \
	  -n mlflow

# Uninstall MLflow
uninstall-mlflow:
	@set -e; \
	helm uninstall mlflow --namespace mlflow || true; \
	kubectl delete service mlflow --namespace mlflow || true
