Kafka can be accessed by consumers via port 9092 on the following DNS name from within your cluster:

    kafka.kafka.svc.cluster.local

Each Kafka broker can be accessed by producers via port 9092 on the following DNS name(s) from within your cluster:

    kafka-controller-0.kafka-controller-headless.kafka.svc.cluster.local:9092
    kafka-controller-1.kafka-controller-headless.kafka.svc.cluster.local:9092
    kafka-controller-2.kafka-controller-headless.kafka.svc.cluster.local:9092

The CLIENT listener for Kafka client connections from within your cluster have been configured with the following security settings:
    - SASL authentication

To connect a client to your Kafka, you need to create the 'client.properties' configuration files with the content below:

security.protocol=SASL_PLAINTEXT
sasl.mechanism=SCRAM-SHA-256
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="user1" \
    password="$(kubectl get secret kafka-user-passwords --namespace kafka -o jsonpath='{.data.client-passwords}' | base64 -d | cut -d , -f 1)";

To create a pod that you can use as a Kafka client run the following commands:

    kubectl run kafka-client --restart='Never' --image docker.io/bitnami/kafka:4.0.0-debian-12-r0 --namespace kafka --command -- sleep infinity
    kubectl cp --namespace kafka /path/to/client.properties kafka-client:/tmp/client.properties
    kubectl exec --tty -i kafka-client --namespace kafka -- bash

    PRODUCER:
        kafka-console-producer.sh \
            --producer.config /tmp/client.properties \
            --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
            --topic test

    CONSUMER:
        kafka-console-consumer.sh \
            --consumer.config /tmp/client.properties \
            --bootstrap-server kafka.kafka.svc.cluster.local:9092 \
            --topic test \
            --from-beginning


# Deploy Airflow On Kubernetes

This guide walks you through installing Airflow using Helm with external PostgreSQL and Redis services instead of the built-in database and message broker.


## Prerequisites

Before starting, ensure that the following tools are installed:
- Kubernetes cluster up and running
- kubectl for interacting with the cluster
- Helm for managing Kubernetes applications
- Make (GNU Make) for automating build and deployment tasks

Ensure you are in the root directory of the project before running these commands


## Create Kubernetes Namespace for Airflow

```bash
kubectl create namespace airflow & kubectl config set-context --current --namespace=airflow
```


## Configure the Bitnami Helm Repository

The Bitnami Helm repository provides a wide range of Helm charts. Add the repository and update your local chart list to install PostgreSQL and Redis as external services for Airflow:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Validate the repo contents using helm search
helm search repo bitnami

#The response should resemble the following:
NAME                                        	CHART VERSION	APP VERSION  	DESCRIPTION                                       
bitnami/airflow                             	22.7.2       	2.10.5       	Apache Airflow is a tool to express and execute...
bitnami/apache                              	11.3.5       	2.4.63       	Apache HTTP Server is an open-source HTTP serve...
bitnami/apisix                              	4.2.2        	3.12.0       	Apache APISIX is high-performance, real-time AP...
# and more
```


## Download PostgreSQL and Redis values.yaml file

```bash
curl -sLo infra/services/airflow/postgresql/values.yaml https://raw.githubusercontent.com/bitnami/charts/master/bitnami/postgresql/values.yaml

curl -sLo infra/services/airflow/redis/values.yaml https://raw.githubusercontent.com/bitnami/charts/master/bitnami/redis/values.yaml
```

Make sure you configure the ``airflow`` user and ``redis`` password correctly in their respective Helm values files to ensure Airflow can connect to its PostgreSQL backend and Redis broker without authentication errors.


## Install PostgreSQL backend database for Airflow

```bash
make -f infra/services/airlow/Makefile install-postgresql-redis

# Verify the PostgreSQL and Redis installation
kubectl get all -n airflow

# The response should resemble the following:
NAME                                     READY   STATUS    RESTARTS        AGE
pod/postgresql-0                         1/1     Running   0               173m
pod/redis-master-0                       1/1     Running   0               174m
pod/redis-replicas-0                     1/1     Running   0               174m

NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
service/postgresql          ClusterIP   10.43.182.85    <none>        5432/TCP            9h
service/postgresql-hl       ClusterIP   None            <none>        5432/TCP            9h
service/redis-headless      ClusterIP   None            <none>        6379/TCP            9h
service/redis-master        ClusterIP   10.43.84.123    <none>        6379/TCP            9h
service/redis-replicas      ClusterIP   10.43.179.38    <none>        6379/TCP            9h

NAME                                 READY   AGE
statefulset.apps/postgresql          1/1     9h
statefulset.apps/redis-master        1/1     9h
statefulset.apps/redis-replicas      1/1     9h
```


## Configure the Airflow Helm Repository

Add the Airflow Helm repository and update the chart list:

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

# Validate the repo contents using helm search
helm search repo apache-airflow

#The response should resemble the following:
NAME                  	CHART VERSION	APP VERSION	DESCRIPTION                                       
apache-airflow/airflow	1.16.0       	2.10.5     	The official Helm chart to deploy Apache Airflo...
```


## Download Airflow values.yaml file

```bash
curl -sLo values.yaml https://raw.githubusercontent.com/apache/airflow/helm-chart/main/chart/values.yaml
```

Then, apply the following changes to your values.yaml:
- Update PostgreSQL connection and Redis brokerUrl to point to your own external services.
- Disable the built-in postgresql and redis components.
- Generate a Fernet key using:
  ```bash
  python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
  and set the result under fernetKey in your config.
- Enable GitSync to automatically pull DAGs from your Git repository.


## Install Airflow

```bash
make -f infra/services/airflow/Makefile install-airflow

# Verify the Airflow installation
kubectl get all

# The response should resemble the following:
NAME                                     READY   STATUS    RESTARTS        AGE
pod/airflow-scheduler-5dd66c9ffb-rvnxd   3/3     Running   0               7h56m
pod/airflow-statsd-688b56dc48-dpb9d      1/1     Running   0               9h
pod/airflow-triggerer-0                  3/3     Running   0               7h56m
pod/airflow-webserver-6879698f59-9csgz   1/1     Running   0               7h56m
pod/airflow-worker-0                     3/3     Running   0               7h56m

NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
service/airflow-statsd      ClusterIP   10.43.47.44     <none>        9125/UDP,9102/TCP   9h
service/airflow-triggerer   ClusterIP   None            <none>        8794/TCP            9h
service/airflow-webserver   ClusterIP   10.43.126.11    <none>        8080/TCP            9h
service/airflow-worker      ClusterIP   None            <none>        8793/TCP            9h

NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/airflow-scheduler   1/1     1            1           9h
deployment.apps/airflow-statsd      1/1     1            1           9h
deployment.apps/airflow-webserver   1/1     1            1           9h

NAME                                           DESIRED   CURRENT   READY   AGE
replicaset.apps/airflow-scheduler-5dd66c9ffb   1         1         1       7h56m
replicaset.apps/airflow-scheduler-78d6f5c844   0         0         0       9h
replicaset.apps/airflow-statsd-688b56dc48      1         1         1       9h
replicaset.apps/airflow-webserver-54bfbcc875   0         0         0       9h
replicaset.apps/airflow-webserver-6879698f59   1         1         1       7h56m

NAME                                 READY   AGE
statefulset.apps/airflow-triggerer   1/1     9h
statefulset.apps/airflow-worker      1/1     9h
```

## Accessing Airflow Web UI via Port Forwarding

To access the Airflow Web UI from your local machine, you can port-forward the service to a local port:

```bash
# Forward Airflow Web UI service to localhost:8080
kubectl port-forward service/airflow-webserver 8080:8080 -n airflow
```

Once the port forwarding is active, you can open ``http://localhost:8080`` in your browser to access the Airflow dashboard.