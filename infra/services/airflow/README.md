## Configure the Airflow Helm Repository

Add the Airflow Helm repository and update the chart list:

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

# Validate the repo contents using helm search
helm search repo apache-airflow

#The response should resemble the following:
NAME                    CHART VERSION   APP VERSION     DESCRIPTION                                       
apache-airflow/airflow  1.15.0          2.9.3           The official Helm chart to deploy Apache Airflo...
```

## Download Airflow values.yaml file

```bash
curl -sLo infra/services/airflow/values.yaml https://raw.githubusercontent.com/apache/airflow/refs/heads/main/chart/values.yaml
```


## Install Airflow

```bash
make -f infra/services/airflow/Makefile install-airflow
```