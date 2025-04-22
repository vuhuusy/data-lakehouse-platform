kubectl create secret generic mysql-secrets --from-literal=mysql-root-password=datahub
kubectl create secret generic neo4j-secrets --from-literal=neo4j-password=datahub

helm repo add datahub https://helm.datahubproject.io/

helm install prerequisites datahub/datahub-prerequisites

helm install datahub datahub/datahub

