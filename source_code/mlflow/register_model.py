from mlflow import register_model
import mlflow

result = mlflow.register_model(
    model_uri=f"runs:/d65ba977ee4943de80f89c2851978926/model",
    name="fraud_detection"
)
