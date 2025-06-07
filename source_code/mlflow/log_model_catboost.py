import mlflow
import mlflow.catboost
import boto3
import joblib
from io import BytesIO
import os

os.environ['MLFLOW_TRACKING_URI'] = 'http://103.82.133.158:30500'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://103.82.133.158:30900'
os.environ["AWS_ACCESS_KEY_ID"] = "minio"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minio123"

# Cấu hình MinIO
s3 = boto3.client(
    's3',
    endpoint_url='https://103.82.133.158:30900',
    aws_access_key_id='minio',
    aws_secret_access_key='minio123',
    verify=False
)

bucket_name = 'mlflow'
object_key = 'fraud_detection/model/catboost/catboost_fraud_model.cbm'

# Tải mô hình CatBoost từ MinIO
response = s3.get_object(Bucket=bucket_name, Key=object_key)
model_data = response['Body'].read()

# Lưu mô hình vào một file tạm thời để load bằng CatBoost
temp_model_path = "/tmp/catboost_fraud_model.cbm"
with open(temp_model_path, 'wb') as f:
    f.write(model_data)

from catboost import CatBoostClassifier

# Load mô hình CatBoost
model = CatBoostClassifier()
model.load_model(temp_model_path)

# Cấu hình tracking URI
mlflow.set_tracking_uri("http://103.82.133.158:30500")

# Tạo experiment nếu chưa tồn tại
experiment_name = "FraudDetection"
mlflow.set_experiment(experiment_name)

# Log mô hình lên MLflow
with mlflow.start_run() as run:
    mlflow.catboost.log_model(model, artifact_path="model")
    print("✅ Model logged to MLflow")
    print("UI:", f"http://103.82.133.158:30500/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")
