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

server:
	@set -e; \
	docker run -p 5001:8080 \
	-e MLFLOW_TRACKING_URI=http://103.82.133.158:30500 \
	-e MLFLOW_S3_ENDPOINT_URL=https://103.82.133.158:30900 \
	-e AWS_ACCESS_KEY_ID=minio \
	-e AWS_SECRET_ACCESS_KEY=minio123 \
	-e MLFLOW_S3_IGNORE_TLS=true \
	-v ~/.mlflow:/root/.mlflow \
	huusy/mlflow:v2.12.1 \
	mlflow models serve -m "runs:/ac6b711d418f48d4abef42374c9b50c2/model" --no-conda --host 0.0.0.0 --port 8080

build-image:
	@set -e; \
	docker build -t huusy/mlflow:v2.12.1 infra/services/mlflow/.

release-image:
	@set -e; \
	docker push huusy/mlflow:v2.12.1
