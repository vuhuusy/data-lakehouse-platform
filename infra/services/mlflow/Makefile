.PHONY: install-mlflow uninstall-mlflow apply-mlflow-service

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
	kubectl apply -f infra/services/mlflow/mlflow-svc.yaml

# Uninstall MLflow
uninstall-mlflow:
	@set -e; \
	helm uninstall mlflow --namespace mlflow || true; \
	kubectl delete service mlflow --namespace mlflow || true
