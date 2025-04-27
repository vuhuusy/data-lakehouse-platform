make -f infra/services/hive/Makefile create-namespace
make -f infra/services/hive/Makefile build-metastore-custom-dockerfile
make -f infra/services/hive/Makefile build-schematool-custom-dockerfile
make -f infra/services/hive/Makefile release-docker-images
make -f infra/services/hive/Makefile install