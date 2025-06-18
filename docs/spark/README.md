helm repo add spark-operator https://kubeflow.github.io/spark-operator

make -f infra/services/spark/Makefile build-spark-application-dockerfile

make -f infra/services/spark/Makefile release-docker-image

make -f infra/services/spark/Makefile create-minio-secret

make -f infra/services/spark/Makefile install-spark