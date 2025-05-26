from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import json

def fetch_census_data():
    hook = HttpHook(http_conn_id='census_api_conn', method='GET')
    extra = hook.get_connection('census_api_conn').extra_dejson
    api_key = extra.get("api_key")

    endpoint = "/data/2023/acs/acs5"
    params = {
        "get": "B01003_001E,NAME",
        "for": "zip%20code%20tabulation%20area:*",
        "key": api_key
    }

    response = hook.run(endpoint, data=params)
    data = response.json()
    print(data[:5])  # Print first 5 rows

with DAG("census_api_example",
         start_date=datetime(2024, 1, 1),
         schedule_interval=None,
         catchup=False) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_census',
        python_callable=fetch_census_data
    )
