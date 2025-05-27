from airflow.operators.dummy import DummyOperator
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import sys
sys.path.append("/opt/airflow/dags/repo/source_code/airflow/python")

from census_etl import check_api_availability, extract, transform, write_parquet_to_minio

default_args = {
    'start_date': datetime(2025, 5, 26),
    'retries': 10
}

with DAG(
    dag_id="census_api_etl_pipeline",
    schedule_interval="@yearly",
    catchup=False,
    default_args=default_args,
    tags=["census", "api"]
) as dag:

    def check_api():
        api_key = Variable.get("CENSUS_API_KEY", default_var=None)
        if not check_api_availability(api_key):
            raise ValueError("Census API is not available")

    def extract_and_transform(**context):
        api_key = Variable.get("CENSUS_API_KEY", default_var=None)
        df = extract(api_key)
        df_t = transform(df)
        context['ti'].xcom_push(key="transformed_df", value=df_t.to_json())

    def save_to_minio(**context):
        df_json = context['ti'].xcom_pull(task_ids='extract_transform', key="transformed_df")
        df = pd.read_json(df_json)
        write_parquet_to_minio(
            df=df,
            bucket_name="gold-zone",
            object_name="features/online_store/state_features.parquet",
            minio_endpoint=Variable.get("MINIO_ENDPOINT"),
            access_key=Variable.get("ACCESS_KEY"),
            secret_key=Variable.get("SECRET_KEY"),
            use_ssl=False
        )
    start = DummyOperator(task_id="start")
    check_api_task = PythonOperator(task_id="check_api", python_callable=check_api)
    extract_transform_task = PythonOperator(task_id="extract_transform", python_callable=extract_and_transform)
    save_task = PythonOperator(task_id="save_to_minio", python_callable=save_to_minio)
    end = DummyOperator(task_id="end")

    start >> check_api_task >> extract_transform_task >> save_task >> end
