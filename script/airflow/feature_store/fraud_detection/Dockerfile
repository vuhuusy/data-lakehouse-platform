FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "feast==0.16.1" \
    "pydantic==1.10.13" \
    "click<8.1" \
	"feast_trino" \
    "regex" \
    "pandas" \
    "feast[redis]" \
    "feast[aws]" \
    "git+https://github.com/shopify/feast-trino.git@main"

RUN pip uninstall protobuf -y
RUN pip install protobuf==3.20.3
RUN pip install psycopg2-binary

WORKDIR /app

COPY ./feature_repo/ /app/
