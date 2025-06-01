import pendulum
import yaml
from airflow.models.dag import DAG
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator

with DAG(
    dag_id="kafka_to_delta",
    schedule=None,
    start_date=days_ago(2),
    catchup=False,
    dagrun_timeout=pendulum.duration(minutes=100),
    tags=["kafka_to_delta"],
    template_searchpath=Variable.get("template_searchpath")
) as dag:
    spark_job = SparkKubernetesOperator(
        task_id="kafka_to_delta",
        application_file="spark-jobs/kafka_to_delta.yaml",
        namespace="spark-operator",
        kubernetes_conn_id="kubernetes_default",
        execution_timeout=pendulum.duration(minutes=15)
    )
