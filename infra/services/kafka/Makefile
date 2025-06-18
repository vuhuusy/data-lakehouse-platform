.DEFAULT_GOAL := help

NAMESPACE ?= kafka
KAFKA_OPERATOR ?= bitnami/kafka

# Define phony targets
.PHONY: install uninstall \
	generate-self-signed-cert-keystore-truststore \
	register-self-signed-cert-keystore-truststore \
	install-kafka \
	uninstall-kafka \
	create-kafka-client-pod \
	create-namespace \
	help

install: create-namespace install-kafka

create-namespace:
	@set -e; \
	kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

generate-self-signed-cert-keystore-truststore:
	@set -e; \
	rm -f infra/certs/kafka/*.jks; \
	openssl req -new -x509 -nodes -days 730 -keyout infra/certs/kafka/kafka.key \
		-out infra/certs/kafka/kafka.crt \
		-config infra/certs/kafka/openssl.conf; \
	openssl pkcs12 -export -in infra/certs/kafka/kafka.crt \
		-inkey infra/certs/kafka/kafka.key \
		-out infra/certs/kafka/kafka.p12 \
		-passout pass:changeit -name kafka; \
	keytool -importkeystore -srckeystore infra/certs/kafka/kafka.p12 \
		-destkeystore infra/certs/kafka/kafka.keystore.jks \
		-srcstoretype pkcs12 \
		-deststorepass changeit \
		-srcstorepass changeit \
		-alias kafka -noprompt; \
	rm infra/certs/kafka/kafka.p12; \
	keytool -importcert -alias kafka -file infra/certs/kafka/kafka.crt \
		-keystore infra/certs/kafka/kafka.truststore.jks \
		-storepass changeit -noprompt

register-self-signed-cert-keystore-truststore:
	@set -e; \
	kubectl delete secret kafka-jks --namespace $(NAMESPACE) || true; \
	kubectl create secret generic kafka-jks \
		--from-file=kafka.truststore.jks=infra/certs/kafka/kafka.truststore.jks \
		--from-file=kafka.keystore.jks=infra/certs/kafka/kafka.keystore.jks \
		--namespace $(NAMESPACE)

install-kafka:
	@set -e; \
	helm upgrade --install kafka $(KAFKA_OPERATOR) \
		--namespace $(NAMESPACE) --create-namespace \
		-f infra/services/kafka/operator/values.yaml

uninstall:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		kafka