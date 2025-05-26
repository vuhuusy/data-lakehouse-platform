from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.hooks.http import HttpHook
from datetime import datetime

def fetch_census():
    hook = HttpHook(method='GET', http_conn_id='census_api_conn')
    conn = hook.get_connection(hook.http_conn_id)
    api_key = conn.extra_dejson.get('api_key')

    response = hook.run(
        endpoint='/data/2023/acs/acs5',
        data={
            "get": "B01003_001E,NAME",
            "for": "zip code tabulation area:*",
            "key": api_key
        }
    )
    print(response.json()[:5])

with DAG("census_api_dag", start_date=datetime(2024, 1, 1), schedule_interval=None, catchup=False) as dag:
    t1 = PythonOperator(
        task_id="fetch_data",
        python_callable=fetch_census
    )
