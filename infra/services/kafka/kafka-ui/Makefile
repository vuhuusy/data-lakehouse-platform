.DEFAULT_GOAL := help

.PHONY: install uninstall help

NAMESPACE ?= kafka

install:
	@set -e; \
	printf '\033[1;33mInstalling Kafka UI...\033[0m\n'; \
	kubectl apply -f infra/services/kafka/kafka-ui/secret.yaml; \
	kubectl delete configmap ssl-files -n $(NAMESPACE) || true; \
	kubectl create configmap ssl-files \
		--from-file=kafka.truststore.jks=infra/certs/kafka/kafka.truststore.jks \
		--from-file=kafka.keystore.jks=infra/certs/kafka/kafka.keystore.jks \
		-n $(NAMESPACE); \
	helm repo list | grep -q kafka-ui || helm repo add kafka-ui https://provectus.github.io/kafka-ui-charts; \
	helm repo update; \
	helm upgrade --install kafka-ui kafka-ui/kafka-ui \
		--namespace $(NAMESPACE) \
		-f infra/services/kafka/kafka-ui/ssl-values.yaml; \
	printf '\033[1;32mKafka UI installation complete.\033[0m\n'

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling Kafka UI...\033[0m\n'; \
	helm uninstall kafka-ui -n $(NAMESPACE) || true; \
	kubectl delete configmap ssl-files -n $(NAMESPACE) || true; \
	printf '\033[1;32mKafka UI uninstalled.\033[0m\n'

help:
	@echo "Makefile commands:"
	@echo "  make install    - Install Kafka UI into '$(NAMESPACE)' namespace"
	@echo "  make uninstall  - Uninstall Kafka UI and related configmap"
