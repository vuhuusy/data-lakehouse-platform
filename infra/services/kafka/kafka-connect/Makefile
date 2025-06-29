NAMESPACE ?= kafka
CONNECT_HOST ?= 103.179.172.171:30083

.PHONY: \
	install uninstall \
	create-namespace \
	install-kafka-connect \
	build-custom-dockerfile release-docker-image \
	list-plugins create-postgres-connector delete-postgres-connector get-all-connectors \
	expose-nodeport help

install: create-namespace install-kafka-connect expose-nodeport

create-namespace:
	@kubectl get namespace $(NAMESPACE) >/dev/null 2>&1 || \
	kubectl create namespace $(NAMESPACE)

install-kafka-connect:
	@set -e; \
	printf '\033[1;33mInstalling Kafka Connect...\033[0m\n'; \
	helm upgrade --install kafka-connect \
		infra/services/kafka/kafka-connect/ \
		--namespace $(NAMESPACE) \
		-f infra/services/kafka/kafka-connect/values.yaml; \
	printf '\033[1;32mKafka Connect installed.\033[0m\n'

uninstall:
	@set -e; \
	printf '\033[1;33mUninstalling Kafka Connect...\033[0m\n'; \
	helm uninstall kafka-connect --namespace $(NAMESPACE) || true; \
	printf '\033[1;32mKafka Connect uninstalled.\033[0m\n'

expose-nodeport:
	@set -e; \
	printf '\033[1;33mExposing Kafka Connect via NodePort...\033[0m\n'; \
	kubectl apply -f infra/services/kafka/kafka-connect/kafka-connect-nodeport.yaml; \
	printf '\033[1;32mNodePort service created.\033[0m\n'

build-custom-dockerfile:
	@set -e; \
	printf '\033[1;33mBuilding Kafka Connect Docker image...\033[0m\n'; \
	docker build \
		-t huusy/cp-kafka-connect:7.9.0 \
		-f infra/services/kafka/kafka-connect/Dockerfile .; \
	printf '\033[1;32mImage built.\033[0m\n'

release-docker-image:
	@set -e; \
	printf '\033[1;33mPushing Kafka Connect Docker image...\033[0m\n'; \
	docker push huusy/cp-kafka-connect:7.9.0; \
	printf '\033[1;32mImage pushed.\033[0m\n'

list-plugins:
	@set -e; \
	printf '\033[1;33mListing available connector plugins...\033[0m\n'; \
	curl -sS http://$(CONNECT_HOST)/connector-plugins

create-postgres-connector:
	@set -e; \
	printf '\033[1;33mCreating Postgres connector...\033[0m\n'; \
	curl -i -X POST \
		-H "Accept:application/json" \
		-H "Content-Type:application/json" \
		http://$(CONNECT_HOST)/connectors/ \
		-d @infra/services/kafka/kafka-connect/postgres-connector.json

delete-postgres-connector:
	@set -e; \
	printf '\033[1;33mDeleting Postgres connector...\033[0m\n'; \
	curl -i -X DELETE \
		http://$(CONNECT_HOST)/connectors/financial-ops-connector

get-all-connectors:
	@set -e; \
	printf '\033[1;33mGetting all connectors...\033[0m\n'; \
	curl -i -X GET http://$(CONNECT_HOST)/connectors

help:
	@echo "Makefile commands:"
	@echo "  make install                             - Install Kafka Connect and expose NodePort"
	@echo "  make uninstall                           - Uninstall Kafka Connect"
	@echo "  make create-namespace                    - Create namespace $(NAMESPACE)"
	@echo "  make build-custom-dockerfile             - Build Kafka Connect Docker image"
	@echo "  make release-docker-image                - Push Docker image to registry"
	@echo "  make list-plugins                        - List connector plugins (CONNECT_HOST=$(CONNECT_HOST))"
	@echo "  make create-postgres-connector           - Create Postgres connector (CONNECT_HOST=$(CONNECT_HOST))"
	@echo "  make delete-postgres-connector           - Delete Postgres connector"
	@echo "  make get-all-connectors                  - List all registered connectors"