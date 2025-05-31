import mlflow
import mlflow.sklearn
import joblib

model = joblib.load("model.pkl")

with mlflow.start_run():
    mlflow.sklearn.log_model(model, artifact_path="model")
