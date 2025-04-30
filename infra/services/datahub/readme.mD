kubectl create secret generic mysql-secrets --from-literal=mysql-root-password=datahub -n datahub
kubectl create secret generic neo4j-secrets --from-literal=neo4j-password=datahub -n datahub

helm install datahub-prerequisites datahub/datahub-prerequisites -n datahub

helm install datahub datahub/datahub -n datahub

make -f infra/services/datahub/Makefile create-secrets
make -f infra/services/datahub/Makefile install
make -f infra/services/datahub/Makefile create-web-nodeport