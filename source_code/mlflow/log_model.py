import mlflow
import mlflow.sklearn
import boto3
import joblib
from io import BytesIO
import os

os.environ['MLFLOW_TRACKING_URI'] = 'http://103.82.20.169:30500'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://103.82.20.169:30900'
os.environ["AWS_ACCESS_KEY_ID"] = "minio"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minio123"

# Cấu hình MinIO
s3 = boto3.client(
    's3',
    endpoint_url='https://103.82.20.169:30900',
    aws_access_key_id='minio',
    aws_secret_access_key='minio123',
    verify=False
)

bucket_name = 'mlflow'
object_key = 'model/fraud_detection/lgbm_model.pkl'

# Tải mô hình từ MinIO
response = s3.get_object(Bucket=bucket_name, Key=object_key)
model_data = response['Body'].read()
model = joblib.load(BytesIO(model_data))

# Cấu hình tracking URI
mlflow.set_tracking_uri("http://103.82.20.169:30500")

# Tạo experiment nếu chưa tồn tại
experiment_name = "FraudDetection"
mlflow.set_experiment(experiment_name)

# Log model lên MLflow
with mlflow.start_run() as run:
    mlflow.sklearn.log_model(model, artifact_path="model")
    print("✅ Model logged to MLflow")
    print("UI:", f"http://103.82.20.169:30500/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")
