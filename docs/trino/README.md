make -f infra/services/trino/Makefile build-trino-custom-dockerfile
make -f infra/services/trino/Makefile release-docker-images
make -f infra/services/trino/Makefile install
make -f infra/services/trino/Makefile create-coordinator-nodeport