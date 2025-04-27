.PHONY: install-kafka-ui uninstall-kafka-ui

# Install Kafka UI
install-kafka-ui:
	@set -e; \
	kubectl delete configmap ssl-files --namespace $(NAMESPACE) || true; \
	kubectl create configmap ssl-files \
		--from-file=kafka.truststore.jks=infra/services/kafka/kafka.truststore.jks \
		--from-file=kafka.keystore.jks=infra/services/kafka/kafka.keystore.jks \
		-n $(NAMESPACE); \
	helm upgrade --install kafka-ui kafka-ui/kafka-ui \
		--namespace $(NAMESPACE) \
		-f infra/services/kafka/kafka-ui/ssl-values.yaml

# Uninstall Kafka UI
uninstall-kafka-ui:
	@set -e; \
	helm uninstall kafka-ui --namespace $(NAMESPACE) || true; \
	kubectl delete configmap ssl-files --namespace $(NAMESPACE) || true
