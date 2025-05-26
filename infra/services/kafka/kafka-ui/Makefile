.PHONY: install-kafka-ui uninstall-kafka-ui
NAMESPACE ?= kafka

# Install Kafka UI
install-kafka-ui:
	@set -e; \
	kubectl apply -f secret.yaml
	kubectl delete configmap ssl-files -n $(NAMESPACE) || true; \
	kubectl create configmap ssl-files \
		--from-file=kafka.truststore.jks=infra/services/kafka/certs/kafka.truststore.jks \
		--from-file=kafka.keystore.jks=infra/services/kafka/certs/kafka.keystore.jks \
		-n $(NAMESPACE); \
	helm upgrade --install kafka-ui kafka-ui/kafka-ui \
		-n $(NAMESPACE) \
		-f infra/services/kafka/kafka-ui/ssl-values.yaml

# Uninstall Kafka UI
uninstall-kafka-ui:
	@set -e; \
	helm uninstall kafka-ui -n $(NAMESPACE) || true; \
	kubectl delete configmap ssl-files -n $(NAMESPACE) || true
