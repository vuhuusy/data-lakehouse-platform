# Makefile for Kafka Connect

NAMESPACE ?= kafka

# Optional targets for specific components
.PHONY: install uninstall build-custom-dockerfile list-plugins create-postgres-connector

build-custom-dockerfile:
	@set -e; \
	docker build --progress=plain \
		-t huusy/kafka-connect:7.9.0 \
		-f infra/services/kafka/kafka-connect/Dockerfile .

install:
	@set -e; \
	helm upgrade --install --namespace $(NAMESPACE) \
		kafka-connect infra/services/kafka/kafka-connect/ \
		--set configurationOverrides.key\\.converter=org.apache.kafka.connect.json.JsonConverter \
		--set configurationOverrides.value\\.converter=org.apache.kafka.connect.json.JsonConverter \
		--set configurationOverrides.security\\.protocol=SASL_PLAINTEXT \
		--set configurationOverrides.sasl\\.mechanism=PLAIN \
		--set configurationOverrides.sasl\\.jaas\\.config="org.apache.kafka.common.security.scram.ScramLoginModule required username=\"user1\" password=\"MMOKgCFj2U\";" \
		--set configurationOverrides.ssl\\.truststore\\.type=JKS \
		--set configurationOverrides.ssl\\.truststore\\.location=/usr/share/confluent-hub-components/kafka.truststore.jks \
		--set configurationOverrides.ssl\\.truststore\\.password=changeit \
		--set configurationOverrides.ssl\\.keystore\\.type=JKS \
		--set configurationOverrides.ssl\\.keystore\\.location=/usr/share/confluent-hub-components/kafka.keystore.jks \
		--set configurationOverrides.ssl\\.keystore\\.password=changeit \
		--set configurationOverrides.connector\\.client\\.config\\.override\\.policy=All \
		--set kafka.bootstrapServers=SASL_PLAINTEXT://kafka-operator.kafka.svc.cluster.local:9092 \
		--set image=huusy/kafka-connect \
		--set imageTag=7.9.0

uninstall:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		kafka-connect

list-plugins:
	@set -e; \
	curl -sS localhost:8083/connector-plugins

create-postgres-connector:
	@set -e; \
	curl -i -X POST \
		-H "Accept:application/json" \
		-H  "Content-Type:application/json" \
		http://localhost:8083/connectors/ -d @infra/services/kafka/kafka-connect/postgres-connector.json

delete-postgres-connector:
	@set -e; \
	curl -i -X DELETE \
		http://localhost:8083/connectors/inventory-connector

get-all-connectors:
	@set -e; \
	curl -i -X GET http://localhost:8083/connectors/