from mlflow.tracking import MlflowClient
client = MlflowClient()
client.transition_model_version_stage(
    name="FraudDetectionXGBoost",
    version=1,
    stage="Production"  # hoặc "Staging"
)
