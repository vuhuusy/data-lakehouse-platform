from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from datetime import datetime
import sys

sys.path.append("/opt/airflow/dags/repo/source_code/airflow/dags")

default_args = {
    'start_date': datetime(2025, 6, 1),
    'retries': 10
}

with DAG(
    dag_id="dag_cal_customer_and_merchant_features_daily",
    schedule_interval='5 0 * * *',
    catchup=False,
    default_args=default_args,
    tags=["features", "feature_store", "daily", "customer", "merchant"],
) as dag:
    spark_job = SparkKubernetesOperator(
        task_id="cal_customer_and_merchant_features_daily",
        application_file="spark-jobs/cal_features_daily.yaml",
        namespace="spark-operator",
        kubernetes_conn_id="kubernetes_default"
    )

    feast_materialize = BashOperator(
        task_id="materialize_features_to_online_store",
        bash_command=(
            "source /opt/airflow/dags/repo/source_code/airflow/feature_store/fraud_detection/venv/bin/activate && "
            "cd /opt/airflow/dags/repo/source_code/airflow/feature_store/fraud_detection/feature_repo && "
            "feast materialize-incremental {{ ds }}"
        )
    )

    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")

    start >> spark_job >> feast_materialize >> end