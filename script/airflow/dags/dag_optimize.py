from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import datetime
import pendulum
import sys

sys.path.append("/opt/airflow/dags/repo/script/airflow/dags")

default_args = {
    'start_date': datetime(2025, 6, 1),
    'retries': 10
}

with DAG(
    dag_id="dag_optimize_partition",
    schedule_interval='5 * * * *',
    start_date=pendulum.datetime(2025, 6, 11, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    default_args=default_args,
    tags=["optimize", "partition"],
) as dag:
    spark_job = SparkKubernetesOperator(
        task_id="optimize_partition",
        application_file="spark-jobs/optimize.yaml",
        namespace="spark-operator",
        kubernetes_conn_id="kubernetes_default"
    )

    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")

    start >> spark_job >> end
