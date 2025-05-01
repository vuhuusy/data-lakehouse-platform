import pendulum

from airflow.models.dag import DAG
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator

with DAG(
    dag_id="spark-pi",
    schedule=None,
    start_date=days_ago(2),
    catchup=False,
    dagrun_timeout=pendulum.duration(minutes=1),
    tags=["spark-pi"],
  #  template_searchpath=Variable.get("template_searchpath")
) as dag:
    spark_job = SparkKubernetesOperator(
        task_id="spark-job",
        application_file="spark-jobs/spark-pi.yaml",
        namespace="spark-jobs",
        kubernetes_conn_id="kubernetes_default"
    )
