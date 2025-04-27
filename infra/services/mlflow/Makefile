.PHONY: install-mlflow uninstall-mlflow

# Install MLflow
install-mlflow:
	@set -e; \
	kubectl get namespace mlflow >/dev/null 2>&1 || kubectl create namespace mlflow; \
	helm upgrade --install mlflow community-charts/mlflow \
		--namespace mlflow \
		-f infra/services/mlflow/values.yaml

# Uninstall MLflow
uninstall-mlflow:
	@set -e; \
	helm uninstall mlflow --namespace mlflow || true
