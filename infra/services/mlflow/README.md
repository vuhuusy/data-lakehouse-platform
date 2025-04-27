helm repo add community-charts https://community-charts.github.io/helm-charts
helm repo update

helm install mlflow community-charts/mlflow -f infra/services/mlflow/values.yaml -n mlflow
