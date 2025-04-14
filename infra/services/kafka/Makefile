.DEFAULT_GOAL := help

# Variables
NAMESPACE ?= kafka
KAFKA_OPERATOR ?= bitnami/kafka
STORE_PASSWORD ?= changeit

# Define phony targets
.PHONY: \
	generate-self-signed-cert-keystore-truststore \
	register-self-signed-cert-keystore-truststore \
	install-kafka \
	uninstall-kafka \
	create-kafka-client-pod \
	help

# Generate self-signed certificate and keystore/truststore
generate-self-signed-cert-keystore-truststore:
	@set -e; \
	rm -f infra/services/kafka/certs/*.jks; \
	openssl req -new -x509 -nodes -days 730 -keyout infra/services/kafka/certs/kafka.key \
		-out infra/services/kafka/certs/kafka.crt \
		-config infra/services/kafka/certs/openssl.conf; \
	openssl pkcs12 -export -in infra/services/kafka/certs/kafka.crt \
		-inkey infra/services/kafka/certs/kafka.key \
		-out infra/services/kafka/certs/kafka.p12 \
		-passout pass:$(STORE_PASSWORD) -name kafka; \
	keytool -importkeystore -srckeystore infra/services/kafka/certs/kafka.p12 \
		-destkeystore infra/services/kafka/certs/kafka.keystore.jks \
		-srcstoretype pkcs12 \
		-deststorepass $(STORE_PASSWORD) \
		-srcstorepass $(STORE_PASSWORD) \
		-alias kafka -noprompt; \
	rm infra/services/kafka/certs/kafka.p12; \
	keytool -importcert -alias kafka -file infra/services/kafka/certs/kafka.crt \
		-keystore infra/services/kafka/certs/kafka.truststore.jks \
		-storepass $(STORE_PASSWORD) -noprompt

# Register self-signed certificate and keystore/truststore in Kubernetes
register-self-signed-cert-keystore-truststore:
	@set -e; \
	kubectl delete secret kafka-jks --namespace $(NAMESPACE) || true; \
	kubectl create secret generic kafka-jks \
		--from-file=kafka.truststore.jks=infra/services/kafka/certs/kafka.truststore.jks \
		--from-file=kafka.keystore.jks=infra/services/kafka/certs/kafka.keystore.jks \
		--namespace $(NAMESPACE)

# Install Kafka
install-kafka:
	@set -e; \
	helm upgrade --install kafka $(KAFKA_OPERATOR) \
		--namespace $(NAMESPACE) --create-namespace


# Uninstall Kafka
uninstall:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		kafka

# Create Kafka client pod
create-kafka-client-pod:
	@set -e; \
	kubectl delete pod kafka-client -n $(NAMESPACE) || true; \
	kubectl run kafka-client \
		--restart='Never' \
		--image docker.io/bitnami/kafka:4.0.0-debian-12-r0 \
		-n $(NAMESPACE) --command -- sleep infinity; \
	sleep 5; \
	kubectl cp -n $(NAMESPACE) \
		infra/services/kafka/client.properties kafka-client:/tmp/client.properties; \
	kubectl cp -n $(NAMESPACE) \
		infra/services/kafka/certs/kafka.truststore.jks kafka-client:/tmp/kafka.truststore.jks; \
	kubectl cp -n $(NAMESPACE) \
		infra/services/kafka/certs/kafka.keystore.jks kafka-client:/tmp/kafka.keystore.jks; \
	kubectl exec --tty -i \
		kafka-client \
		-n $(NAMESPACE) -- bash

help:
	@echo ""
	@echo "Available targets:"
	@echo "  generate-self-signed-cert-keystore-truststore   Generate SSL cert + keystore/truststore"
	@echo "  register-self-signed-cert-keystore-truststore   Register certs as Kubernetes secret"
	@echo "  install-kafka                                    Install Kafka using Helm"
	@echo "  uninstall-kafka                                  Uninstall Kafka release"
	@echo "  create-kafka-client-pod                          Create interactive Kafka client pod"
	@echo ""