FROM ghcr.io/mlflow/mlflow:v2.12.1

RUN apt-get update && apt-get install -y libgomp1

RUN pip install boto3 lightgbm==4.3.0 pandas==2.2.2 numpy==2.3.0 \
    scikit-learn==1.4.2 matplotlib==3.8.4 scipy==1.15.3 \
    pyarrow==19.0.1 cloudpickle==3.1.1 mlflow==2.22.1 catboost==1.2.8 gunicorn xgboost==2.0.3
