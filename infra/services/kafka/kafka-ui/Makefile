.PHONY: install uninstall
NAMESPACE ?= kafka

# Install Kafka UI
install:
	@set -e; \
	kubectl apply -f infra/services/kafka/kafka-ui/secret.yaml
	kubectl delete configmap ssl-files -n $(NAMESPACE) || true; \
	kubectl create configmap ssl-files \
		--from-file=kafka.truststore.jks=infra/certs/kafka/kafka.truststore.jks \
		--from-file=kafka.keystore.jks=infra/certs/kafka/kafka.keystore.jks \
		-n $(NAMESPACE); \
	helm upgrade --install kafka-ui kafka-ui/kafka-ui \
		-n $(NAMESPACE) \
		-f infra/services/kafka/kafka-ui/ssl-values.yaml

uninstall:
	@set -e; \
	helm uninstall kafka-ui -n $(NAMESPACE) || true; \
	kubectl delete configmap ssl-files -n $(NAMESPACE) || true
