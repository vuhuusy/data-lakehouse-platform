from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.hooks.http import HttpHook
from datetime import datetime
import pandas as pd
import numpy as np
import os

# State map
STATE_MAP = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID",
    "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
    "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT",
    "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC",
    "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC",
    "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY", "60": "AS", "66": "GU", "69": "MP", "72": "PR",
    "74": "UM", "78": "VI"
}

API_ENDPOINT = "/data/2023/acs/acs5"
VARS = "B01003_001E,B01002_001E,B19013_001E,B17001_002E,B23025_005E"
TEMP_FILE = "/tmp/census_raw.csv"


def check_api_available():
    hook = HttpHook(method='GET', http_conn_id='census_api_conn')
    response = hook.run("/")
    if response.status_code != 200:
        raise Exception("Census API not available")


def extract_data():
    hook = HttpHook(method='GET', http_conn_id='census_api_conn')
    api_key = hook.get_connection('census_api_conn').extra_dejson.get("api_key")

    all_data = []
    for fips, abbrev in STATE_MAP.items():
        params = {
            "get": VARS,
            "for": f"state:{fips}",
            "key": api_key
        }
        response = hook.run(endpoint=API_ENDPOINT, data=params)
        json_data = response.json()
        columns = json_data[0] + ["state_code"]
        for row in json_data[1:]:
            all_data.append(dict(zip(columns, row)))

    df = pd.DataFrame(all_data)
    df.to_csv(TEMP_FILE, index=False)


def transform_data():
    df = pd.read_csv(TEMP_FILE)
    df.columns = [
        "total_population", "median_age", "median_household_income",
        "poverty_count", "unemployment_count", "state_code"
    ]
    df = df.astype(float, errors='ignore')
    df = df[df[[
        "total_population", "median_age", "median_household_income",
        "poverty_count", "unemployment_count"
    ]].gt(0).all(axis=1)]

    df["state"] = df["state_code"].astype(str).str.zfill(2).map(STATE_MAP)
    df["poverty_rate"] = df["poverty_count"] / df["total_population"]
    df["unemployment_rate"] = df["unemployment_count"] / df["total_population"]
    df["median_income_log"] = np.log1p(df["median_household_income"])
    df["income_per_capita"] = df["median_household_income"] / df["total_population"]
    df["high_poverty_flag"] = (df["poverty_rate"] > 0.2).astype(int)
    df["high_unemp_flag"] = (df["unemployment_rate"] > 0.1).astype(int)
    df["age_type"] = pd.cut(df["median_age"], bins=[0, 25, 45, 65, np.inf], labels=["<25", "25–45", "45–65", ">65"])

    df = df[[
        "state", "poverty_rate", "unemployment_rate", "median_income_log",
        "income_per_capita", "high_poverty_flag", "high_unemp_flag", "age_type"
    ]]

    df.to_parquet("/tmp/final_features.parquet", index=False)


def write_parquet_to_minio():
    import boto3
    import pyarrow.parquet as pq
    import pyarrow as pa

    s3 = boto3.client(
        's3',
        endpoint_url="https://minio.minio.svc.cluster.local:443",
        aws_access_key_id="minio",
        aws_secret_access_key="minio123",
        region_name='us-east-1'
    )

    with open("/tmp/final_features.parquet", "rb") as f:
        s3.upload_fileobj(f, "gold-zone", "gold-zone/feature/online/geographic/state_features.parquet")


def cleanup():
    os.remove(TEMP_FILE)
    os.remove("/tmp/final_features.parquet")


def end():
    print("Pipeline completed.")


with DAG("census_geographic_pipeline",
         start_date=datetime(2024, 1, 1),
         schedule_interval=None,
         catchup=False) as dag:

    t1 = PythonOperator(task_id="check_api_available", python_callable=check_api_available)
    t2 = PythonOperator(task_id="extract_data", python_callable=extract_data)
    t3 = PythonOperator(task_id="transform_data", python_callable=transform_data)
    t4 = PythonOperator(task_id="write_parquet_to_minio", python_callable=write_parquet_to_minio)
    t5 = PythonOperator(task_id="cleanup_temp_files", python_callable=cleanup)
    t6 = PythonOperator(task_id="end_pipeline", python_callable=end)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6
