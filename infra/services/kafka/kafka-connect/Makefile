NAMESPACE ?= kafka
CONNECT_HOST ?= 103.179.172.171:30083

.PHONY: install uninstall \
		create-namespace \
		install-kafka-connect \
		build-custom-dockerfile release-docker-image \
		list-plugins create-postgres-connector \
	expose-nodeport

build-custom-dockerfile:
	@set -e; \
	docker build \
		-t huusy/cp-kafka-connect:7.9.0 \
		-f infra/services/kafka/kafka-connect/Dockerfile .

release-docker-image:
	@set -e; \
	docker push huusy/cp-kafka-connect:7.9.0

install-kafka-connect:
	@set -e; \
	helm upgrade --install kafka-connect \
	infra/services/kafka/kafka-connect/ \
	--namespace $(NAMESPACE) \
	-f infra/services/kafka/kafka-connect/values.yaml

install: create-namespace install-kafka-connect expose-nodeport

uninstall:
	@set -e; \
	helm uninstall --namespace $(NAMESPACE) \
		kafka-connect

create-namespace:
	@set -e; \
	kubectl create namespace $(NAMESPACE) || true

expose-nodeport:
	@kubectl apply -f infra/services/kafka/kafka-connect/kafka-connect-nodeport.yaml

list-plugins:
	@set -e; \
	curl -sS http://$(CONNECT_HOST)/connector-plugins

create-postgres-connector:
	@set -e; \
	curl -i -X POST \
		-H "Accept:application/json" \
		-H  "Content-Type:application/json" \
		http://$(CONNECT_HOST)/connectors/ -d @infra/services/kafka/kafka-connect/postgres-connector.json

delete-postgres-connector:
	@set -e; \
	curl -i -X DELETE \
		http://$(CONNECT_HOST)/connectors/financial-ops-connector

get-all-connectors:
	@set -e; \
	curl -i -X GET http://$(CONNECT_HOST)/connectors/
