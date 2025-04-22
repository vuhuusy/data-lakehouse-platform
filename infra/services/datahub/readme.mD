kubectl create secret generic mysql-secrets --from-literal=mysql-root-password=datahub
kubectl create secret generic neo4j-secrets --from-literal=neo4j-password=datahub

helm install datahub-prerequisites datahub/datahub-prerequisites

helm install datahub datahub/datahub

make -f infra/services/datahub/Makefile create-secrets
make -f infra/services/datahub/Makefile install
make -f infra/services/datahub/Makefile create-web-nodeport