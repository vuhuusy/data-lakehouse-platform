helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm search repo spark-operator

make -f infra/services/spark/Makefile install-spark

make -f infra/services/spark/Makefile build-spark-application-dockerfile

make -f infra/services/spark/Makefile release-docker-image