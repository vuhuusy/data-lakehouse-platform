.DEFAULT_GOAL := help

NAMESPACE ?= flink
CHART_FLINK ?= flink-operator-repo/flink-kubernetes-operator

.PHONY: \
	install uninstall \
	create-namespace \
	install-cert-manager \
	install-flink \
	create-secret-kafka \
	create-flink-nodeport \
	build-flink-custom-dockerfile \
	release-docker-images \
	help

install: create-namespace install-flink create-secret-kafka create-flink-nodeport

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling Flink Operator and related resources...\033[0m\n'; \
	helm uninstall --namespace $(NAMESPACE) flink-kubernetes-operator || true; \
	kubectl delete secret kafka-jks -n $(NAMESPACE) || true; \
	kubectl delete -f infra/services/flink/flink-nodeport.yaml -n $(NAMESPACE) || true; \
	printf '\033[1;32mFlink uninstallation complete.\033[0m\n'

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-cert-manager:
	@set -e; \
	printf '\033[1;33mInstalling cert-manager...\033[0m\n'; \
	kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.8.2/cert-manager.yaml; \
	printf '\033[1;32mcert-manager installation complete.\033[0m\n'

install-flink:
	@set -e; \
	printf '\033[1;33mInstalling Flink Kubernetes Operator...\033[0m\n'; \
	helm repo list | grep -q flink-operator-repo || \
		helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.12.0/; \
	helm repo update; \
	helm upgrade --install flink-kubernetes-operator $(CHART_FLINK) \
		--namespace $(NAMESPACE) \
		-f infra/services/flink/values.yaml; \
	printf '\033[1;32mFlink Operator installation complete.\033[0m\n'

create-secret-kafka:
	@set -e; \
	printf '\033[1;33mCreating Kafka JKS secret...\033[0m\n'; \
	kubectl create secret generic kafka-jks \
		--from-file=kafka.crt=infra/certs/kafka/kafka.crt \
		--from-file=kafka.key=infra/certs/kafka/kafka.key \
		--from-file=kafka.keystore.jks=infra/certs/kafka/kafka.keystore.jks \
		--from-file=kafka.truststore.jks=infra/certs/kafka/kafka.truststore.jks \
		-n $(NAMESPACE); \
	printf '\033[1;32mKafka secret created.\033[0m\n'

create-flink-nodeport:
	@set -e; \
	printf '\033[1;33mCreating NodePort service for Flink...\033[0m\n'; \
	kubectl apply -n $(NAMESPACE) -f infra/services/flink/flink-nodeport.yaml; \
	printf '\033[1;32mNodePort service created.\033[0m\n'

build-flink-custom-dockerfile:
	@set -e; \
	printf '\033[1;33mBuilding custom Flink Docker image...\033[0m\n'; \
	docker build \
		-t huusy/flink:1.17 \
		-f infra/services/flink/Dockerfile .; \
	printf '\033[1;32mDocker image built.\033[0m\n'

release-docker-images:
	@set -e; \
	printf '\033[1;33mReleasing Flink Docker image...\033[0m\n'; \
	docker push huusy/flink:1.17; \
	printf '\033[1;32mDocker image pushed to registry.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install                         - Install Flink Operator, secret, NodePort"
	@echo "  make uninstall                       - Uninstall Flink Operator and related resources"
	@echo "  make create-namespace                - Create Kubernetes namespace if not exists"
	@echo "  make install-cert-manager            - Install cert-manager (required by Flink)"
	@echo "  make install-flink                   - Install Flink Kubernetes Operator via Helm"
	@echo "  make create-secret-kafka             - Create Kafka TLS/SSL secret for Flink jobs"
	@echo "  make create-flink-nodeport           - Expose Flink UI via NodePort"
	@echo "  make build-flink-custom-dockerfile   - Build Flink Docker image"
	@echo "  make release-docker-images           - Push Flink Docker image to registry"
