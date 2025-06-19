Assuming kubectl context points to the correct kubernetes cluster, first create kubernetes secrets that contain MySQL and Neo4j passwords.

```bash
kubectl create secret generic mysql-secrets --from-literal=mysql-root-password=datahub -n datahub
kubectl create secret generic neo4j-secrets --from-literal=neo4j-password=datahub -n datahub
```

The above commands sets the passwords to "datahub" as an example. Change to any password of choice.

Add datahub helm repo by running the following

```bash
helm repo add datahub https://helm.datahubproject.io/
```

Then, deploy the dependencies by running the following

```bash
helm upgrade --install prerequisites datahub/datahub-prerequisites \
        --namespace datahub \
        --create-namespace \
        -f infra/services/datahub/prerequisites/values.yaml
```

Run kubectl get pods to check whether all the pods for the dependencies are running. You should get a result similar to below.

```bash
NAME                                               READY   STATUS      RESTARTS   AGE
elasticsearch-master-0                             1/1     Running     0          62m
elasticsearch-master-1                             1/1     Running     0          62m
elasticsearch-master-2                             1/1     Running     0          62m
prerequisites-cp-schema-registry-cf79bfccf-kvjtv   2/2     Running     1          63m
prerequisites-kafka-0                              1/1     Running     2          62m
prerequisites-mysql-0                              1/1     Running     1          62m
prerequisites-neo4j-community-0                    1/1     Running     0          52m
prerequisites-zookeeper-0                          1/1     Running     0          62m
```

deploy Datahub by running the following


```bash
helm upgrade --install datahub datahub/datahub \
        --namespace datahub \
        --create-namespace \
        -f infra/services/datahub/values.yaml
```


make -f infra/services/datahub/Makefile create-secrets
make -f infra/services/datahub/Makefile install
make -f infra/services/datahub/Makefile create-web-nodeport