from airflow.models.dag import DAG
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
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

    feast_apply_materialize = KubernetesPodOperator(
        task_id="feast_apply_materialize",
        name="feast-materialize-job",
        namespace="feast",
        image="huusy/feast:0.16.1",
        image_pull_policy="Always",
        cmds=["bash", "-c"],
        arguments=["feast apply && feast materialize-incremental $(date +%F)T23:59:59"],
        env_vars={  "FEAST_USAGE": "False",
                    "AWS_ACCESS_KEY_ID": "minio",
                    "AWS_SECRET_ACCESS_KEY": "minio123",
                    "AWS_ENDPOINT_URL": "https://minio.minio.svc.cluster.local:443"},
        is_delete_operator_pod=True,
        get_logs=True,
        kubernetes_conn_id="kubernetes_default"
    )

    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")

    start >> spark_job >> feast_apply_materialize >> end
