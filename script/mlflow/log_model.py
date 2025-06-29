import os
import boto3
import joblib
from io import BytesIO
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# ====== CONFIGURATION ======
MLFLOW_TRACKING_URI = "http://mlflow.mlflow.svc.cluster.local:5000"
S3_ENDPOINT = "https://minio.minio.svc.cluster.local:9000"
AWS_ACCESS_KEY_ID = "minio"
AWS_SECRET_ACCESS_KEY = "minio123"

os.environ['MLFLOW_TRACKING_URI'] = MLFLOW_TRACKING_URI
os.environ['MLFLOW_S3_ENDPOINT_URL'] = S3_ENDPOINT
os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY

# ===== Initialize S3 client ======
s3 = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    verify=False
)

# ====== Load model from S3 ======
bucket_name = 'mlflow'
object_key = 'model/fraud_detection/model/xg_classifier.pkl'

response = s3.get_object(Bucket=bucket_name, Key=object_key)
model_data = response['Body'].read()
model = joblib.load(BytesIO(model_data))

# ====== MLFLOW CONFIGURATION ======
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient()

try:
    client._tracking_client.store.artifact_repo.s3_client.meta.config.verify = False
except Exception as e:
    print("Error setting S3 client verification:", e)

# ====== LOG MODEL TO MLFLOW ======
experiment_name = "FraudDetection"
mlflow.set_experiment(experiment_name)

with mlflow.start_run() as run:
    mlflow.sklearn.log_model(model, artifact_path="model")
    print("Model logged to MLflow")
    print(f"UI: {MLFLOW_TRACKING_URI}/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")

    run_id = run.info.run_id

# ====== REGISTER MODEL AND TRANSITION STAGE ======
model_name = "FraudDetectionXGBoost"

# Register model
result = mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name=model_name
)

# Transition model to Production stage
client.transition_model_version_stage(
    name=model_name,
    version=result.version,
    stage="Production"
)

print(f"Model registered as '{model_name}' version {result.version} and moved to 'Production'. Run ID: {run_id}")
