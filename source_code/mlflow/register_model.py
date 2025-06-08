from mlflow import register_model
import mlflow

result = mlflow.register_model(
    model_uri=f"runs:/677f3271b13f445ea17e865c40171965/model",
    name="FraudDetectionCatBoost"
)
