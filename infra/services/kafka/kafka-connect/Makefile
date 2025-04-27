# Makefile for Kafka Connect

NAMESPACE ?= kafka
CONNECT_HOST ?= 103.179.172.171:30083

# Optional targets for specific components
.PHONY: install uninstall build-custom-dockerfile list-plugins create-postgres-connector \
	expose-nodeport

build-custom-dockerfile:
	@set -ex; \
	docker build \
		-t huusy/kafka-connect-custom:7.9.0 \
		-f infra/services/kafka/kafka-connect/Dockerfile .

release-docker-image:
	@set -ex; \
	docker push huusy/kafka-connect-custom:7.9.0

install:
	@set -ex; \
	helm upgrade --install --namespace $(NAMESPACE) \
		kafka-connect infra/services/kafka/kafka-connect/ \
		--set configurationOverrides.key\\.converter=org.apache.kafka.connect.json.JsonConverter \
		--set configurationOverrides.value\\.converter=org.apache.kafka.connect.json.JsonConverter \
		--set configurationOverrides.security\\.protocol=SASL_SSL \
		--set configurationOverrides.sasl\\.mechanism=SCRAM-SHA-512 \
		--set configurationOverrides.sasl\\.jaas\\.config="org.apache.kafka.common.security.scram.ScramLoginModule required username=\"kafka\" password=\"kafka\";" \
		--set configurationOverrides.ssl\\.truststore\\.type=JKS \
		--set configurationOverrides.ssl\\.truststore\\.location=/usr/share/confluent-hub-components/kafka.truststore.jks \
		--set configurationOverrides.ssl\\.truststore\\.password=changeit \
		--set configurationOverrides.ssl\\.keystore\\.type=JKS \
		--set configurationOverrides.ssl\\.keystore\\.location=/usr/share/confluent-hub-components/kafka.keystore.jks \
		--set configurationOverrides.ssl\\.keystore\\.password=changeit \
		--set configurationOverrides.connector\\.client\\.config\\.override\\.policy=All \
		--set kafka.bootstrapServers=SASL_SSL://kafka.kafka.svc.cluster.local:9092 \
		--set image=huusy/kafka-connect-custom \
		--set imageTag=7.9.0

uninstall:
	@set -ex; \
	helm uninstall --namespace $(NAMESPACE) \
		kafka-connect

expose-nodeport:
	@kubectl apply -f infra/services/kafka/kafka-connect/kafka-connect-nodeport.yaml

list-plugins:
	@set -ex; \
	curl -sS http://$(CONNECT_HOST)/connector-plugins

create-postgres-connector:
	@set -ex; \
	curl -i -X POST \
		-H "Accept:application/json" \
		-H  "Content-Type:application/json" \
		http://$(CONNECT_HOST)/connectors/ -d @infra/services/kafka/kafka-connect/postgres-connector.json

delete-postgres-connector:
	@set -ex; \
	curl -i -X DELETE \
		http://$(CONNECT_HOST)/connectors/financial-ops-connector

get-all-connectors:
	@set -ex; \
	curl -i -X GET http://$(CONNECT_HOST)/connectors/
