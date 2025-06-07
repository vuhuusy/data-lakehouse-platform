FROM ghcr.io/mlflow/mlflow:v2.12.1

RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && rm miniconda.sh && \
    /opt/conda/bin/conda install python=3.12


RUN ln -sf /usr/bin/python3.12 /usr/bin/python

RUN apt-get update && apt-get install -y libgomp1

RUN pip install boto3 lightgbm==4.3.0 pandas==2.2.2 numpy==2.3.0 \
    scikit-learn==1.6.1 matplotlib==3.10.3 scipy==1.15.3 \
    pyarrow==19.0.1 cloudpickle==3.1.1 mlflow==2.22.1 catboost==1.2.8 gunicorn xgboost==2.0.3
